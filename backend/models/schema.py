from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator


class SchemaGenerateRequest(BaseModel):
    schema_type: str = Field(..., max_length=100, description="Schema.org type (e.g., Article, Product)")
    content: str = Field(..., min_length=1, max_length=1000000, description="Content to generate schema from")
    url: Optional[str] = Field(None, max_length=2048, description="URL of the content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (max 50 keys)")

    @field_validator('metadata')
    @classmethod
    def validate_metadata_size(cls, v):
        """Limit metadata dictionary size to prevent abuse."""
        if v is not None and len(v) > 50:
            raise ValueError("metadata cannot have more than 50 keys")
        return v


class SchemaValidateRequest(BaseModel):
    schema: Dict[str, Any] = Field(..., description="Schema.org JSON-LD to validate")

    @field_validator('schema')
    @classmethod
    def validate_schema_size(cls, v):
        """Limit schema size to prevent abuse."""
        # Rough estimate: check number of keys at top level
        if len(v) > 100:
            raise ValueError("schema cannot have more than 100 top-level keys")
        return v


class SchemaGenerateResponse(BaseModel):
    schema: Dict[str, Any]
    completeness_score: float
    warnings: List[str]


class SchemaValidateResponse(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    completeness_score: float
    suggestions: List[str]


class StructuredValidationError(BaseModel):
    """Structured validation error with path and code information."""
    path: str = Field(..., description="JSON path to the field with error")
    code: str = Field(..., description="Error code (e.g., MISSING_REQUIRED_FIELD)")
    message: str = Field(..., description="Human-readable error message")
    severity: str = Field(..., description="Error severity (ERROR or WARNING)")


class StructuredSchemaValidateResponse(BaseModel):
    """Validation response with structured error details."""
    is_valid: bool
    errors: List[StructuredValidationError]
    warnings: List[StructuredValidationError]
    completeness_score: float
    suggestions: List[str]

