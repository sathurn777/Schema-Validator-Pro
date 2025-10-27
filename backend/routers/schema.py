from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, Union
import time

from backend.services.schema_generator import SchemaGenerator
from backend.services.schema_validator import SchemaValidator
from backend.dependencies import (
    get_schema_generator,
    get_schema_validator,
)

from backend.models.schema import (
    SchemaGenerateRequest,
    SchemaValidateRequest,
    SchemaGenerateResponse,
    SchemaValidateResponse,
    StructuredSchemaValidateResponse,
    StructuredValidationError,
)
from backend.models.error import (
    ErrorCode,
    ErrorDetail,
    create_error_response,
)
from backend.utils.logger import get_logger, RequestLogger
from backend.middleware.metrics import record_schema_generation, record_error

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/schema", tags=["schema"])



@router.post("/generate", response_model=SchemaGenerateResponse)
async def generate_schema(
    request: SchemaGenerateRequest,
    schema_generator: SchemaGenerator = Depends(get_schema_generator),
    schema_validator: SchemaValidator = Depends(get_schema_validator),
):
    """
    Generate Schema.org JSON-LD markup

    Returns generated schema with completeness score and warnings.
    """
    start_time = time.time()

    try:
        # Log request start
        logger.info(
            "schema_generation_started",
            schema_type=request.schema_type,
            url=request.url,
            has_metadata=bool(request.metadata),
        )

        kwargs = request.metadata or {}
        schema = schema_generator.generate(
            schema_type=request.schema_type,
            content=request.content,
            url=request.url,
            **kwargs,
        )

        # Validate and get warnings
        is_valid, errors, warnings = schema_validator.validate(schema)

        # Calculate completeness score
        completeness_score = schema_validator.calculate_completeness_score(schema)

        # Record metrics
        duration = time.time() - start_time
        record_schema_generation(
            schema_type=request.schema_type,
            duration=duration,
            completeness=completeness_score,
            success=is_valid,
        )

        logger.info(
            "schema_generation_completed",
            schema_type=request.schema_type,
            completeness_score=completeness_score,
            duration_ms=round(duration * 1000, 2),
            warnings_count=len(warnings),
        )

        return SchemaGenerateResponse(
            schema=schema,
            completeness_score=completeness_score,
            warnings=warnings,
        )

    except ValueError as e:
        # Client error - invalid input
        duration = time.time() - start_time

        # Record metrics
        record_schema_generation(
            schema_type=request.schema_type,
            duration=duration,
            completeness=0,
            success=False,
        )
        record_error(error_type="ValueError", error_code="invalid_schema_type")

        logger.warning(
            "schema_generation_invalid_request",
            schema_type=request.schema_type,
            error=str(e),
            duration_ms=round(duration * 1000, 2),
        )

        error_response = create_error_response(
            error_code=ErrorCode.INVALID_SCHEMA_TYPE,
            message=str(e),
            details=[ErrorDetail(
                field="schema_type",
                message=str(e),
                code="invalid_value",
                value=request.schema_type,
            )]
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response.model_dump()
        )

    except Exception as e:
        # Server error - unexpected
        duration = time.time() - start_time

        # Record metrics
        record_schema_generation(
            schema_type=request.schema_type,
            duration=duration,
            completeness=0,
            success=False,
        )
        record_error(error_type=type(e).__name__, error_code="internal_error")

        logger.error(
            "schema_generation_failed",
            schema_type=request.schema_type,
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=round(duration * 1000, 2),
            exc_info=True,
        )

        error_response = create_error_response(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred while generating schema",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


@router.post("/validate", response_model=Union[SchemaValidateResponse, StructuredSchemaValidateResponse])
async def validate_schema(
    request: SchemaValidateRequest,
    structured: bool = Query(False, description="Return structured error details with path and code"),
    schema_validator: SchemaValidator = Depends(get_schema_validator),
):
    """
    Validate Schema.org JSON-LD markup and return validation details.

    Args:
        request: Schema validation request containing the schema to validate
        structured: If True, return structured error details with path/code/severity.
                   If False (default), return simple string lists for backward compatibility.
        schema_validator: Injected schema validator instance

    Returns:
        SchemaValidateResponse (default) or StructuredSchemaValidateResponse (when structured=True)
    """
    try:
        # Create validator with appropriate structured_errors setting
        if structured:
            # For structured mode, create a new validator instance with structured_errors=True
            from backend.registry.schema_registry import SCHEMA_REGISTRY
            structured_validator = SchemaValidator(structured_errors=True, registry=SCHEMA_REGISTRY)
            result = structured_validator.validate(request.schema)

            # result is a dict with structured errors
            logger.info(
                f"Validated schema (structured): valid={result['is_valid']}, "
                f"completeness={result['completeness_score']}%, "
                f"errors={len(result['errors'])}, warnings={len(result['warnings'])}"
            )

            return StructuredSchemaValidateResponse(
                is_valid=result['is_valid'],
                errors=[StructuredValidationError(**e) for e in result['errors']],
                warnings=[StructuredValidationError(**w) for w in result['warnings']],
                completeness_score=result['completeness_score'],
                suggestions=result['suggestions'],
            )
        else:
            # Default mode: backward compatible string lists
            is_valid, errors, warnings = schema_validator.validate(request.schema)
            completeness_score = schema_validator.calculate_completeness_score(request.schema)
            suggestions = schema_validator.get_optimization_suggestions(request.schema)

            logger.info(
                f"Validated schema: valid={is_valid}, completeness={completeness_score}%, "
                f"errors={len(errors)}, warnings={len(warnings)}"
            )

            return SchemaValidateResponse(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                completeness_score=completeness_score,
                suggestions=suggestions,
            )

    except Exception as e:
        logger.error(f"Unexpected error validating schema: {e}", exc_info=True)
        error_response = create_error_response(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred while validating schema",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump()
        )


@router.get("/types")
async def get_schema_types(schema_generator: SchemaGenerator = Depends(get_schema_generator)):
    """Get list of supported schema types."""
    types = schema_generator.get_supported_types()
    return {"types": types, "count": len(types)}


@router.get("/template/{schema_type}")
async def get_schema_template(
    schema_type: str,
    schema_generator: SchemaGenerator = Depends(get_schema_generator),
):
    """Get template definition for a schema type."""
    try:
        template = schema_generator.get_template(schema_type)
        return {"schema_type": schema_type, "template": template}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": str(e),
                "supported_types": schema_generator.get_supported_types(),
            },
        )

