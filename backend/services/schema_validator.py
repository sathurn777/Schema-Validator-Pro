"""
Schema Validator Service - Schema Validator Pro
Validates Schema.org markup and provides optimization suggestions.

Features:
- Validates required and optional fields
- Checks field types and values
- Provides optimization suggestions
- Calculates completeness score
- Deep validation for nested objects (Offer, Address, Rating, etc.)
- Structured error output with field paths and error codes
- Zero-cost implementation (no external APIs required)
"""

from typing import Dict, List, Tuple, Any, Optional, Union
from backend.registry.schema_registry import SchemaRegistry, SCHEMA_REGISTRY


class ValidationError:
    """Structured validation error with field path and error code."""

    def __init__(
        self,
        path: str,
        code: str,
        message: str,
        severity: str = "ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        self.path = path
        self.code = code
        self.message = message
        self.severity = severity
        self.message_key = self._get_message_key(code, severity)
        self.context = context or {}

    def _get_message_key(self, code: str, severity: str) -> str:
        """Convert error code to i18n message key."""
        return f"{'error' if severity == 'ERROR' else 'warning'}.{code.lower()}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "path": self.path,
            "code": self.code,
            "message": self.message,
            "message_key": self.message_key,
            "severity": self.severity
        }
        if self.context:
            result["context"] = self.context
        return result

    def to_string(self) -> str:
        """Convert to simple string for backward compatibility."""
        return self.message


class SchemaValidator:
    """
    Schema.org validator with comprehensive validation rules.
    Provides detailed error messages and optimization suggestions.
    Supports structured error output with field paths and error codes.
    """

    def __init__(self, structured_errors: bool = False, registry: Optional[SchemaRegistry] = SCHEMA_REGISTRY):
        """
        Initialize validator.

        Args:
            structured_errors: If True, return structured ValidationError objects.
                             If False (default), return simple string lists for backward compatibility.
            registry: SchemaRegistry instance to read rules from. Defaults to global SCHEMA_REGISTRY.
        """
        self.structured_errors = structured_errors
        self.registry: SchemaRegistry = registry if registry is not None else SCHEMA_REGISTRY

    # Schema.org required fields definition
    REQUIRED_FIELDS = {
        "Article": ["@context", "@type", "headline", "author"],
        "Product": ["@context", "@type", "name"],
        "Organization": ["@context", "@type", "name"],
        "Event": ["@context", "@type", "name", "startDate", "location"],
        "Person": ["@context", "@type", "name"],
        "Recipe": ["@context", "@type", "name", "recipeIngredient", "recipeInstructions"],
        "FAQPage": ["@context", "@type", "mainEntity"],
        "HowTo": ["@context", "@type", "name", "step"],
        "Course": ["@context", "@type", "name", "description", "provider"]
    }

    # Recommended optional fields for better SEO
    RECOMMENDED_FIELDS = {
        "Article": ["image", "datePublished", "publisher", "description"],
        "Product": ["image", "brand", "offers", "aggregateRating", "review"],
        "Organization": ["url", "logo", "description"],
        "Event": ["image", "description", "offers", "organizer"],
        "Person": ["url", "image", "jobTitle"],
        "Recipe": ["image", "author", "prepTime", "cookTime", "aggregateRating"],
        "FAQPage": ["description", "name"],
        "HowTo": ["image", "description", "totalTime"],
        "Course": ["url", "offers", "aggregateRating"]
    }

    def validate(self, schema: Dict[str, Any]) -> Union[Tuple[bool, List[str], List[str]], Dict[str, Any]]:
        """
        Validate Schema.org markup.

        Args:
            schema: Schema.org JSON-LD dictionary

        Returns:
            If structured_errors=False (default):
                Tuple of (is_valid, errors, warnings)
                - is_valid: True if schema passes validation
                - errors: List of error messages (critical issues)
                - warnings: List of warning messages (recommendations)

            If structured_errors=True:
                Dict with keys:
                - is_valid: bool
                - errors: List[ValidationError]
                - warnings: List[ValidationError]
                - completeness_score: float
                - suggestions: List[str]
        """
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []

        # 1. Check basic structure
        if "@context" not in schema:
            errors.append(ValidationError(
                path="",
                code="MISSING_CONTEXT",
                message="Missing @context field",
                severity="ERROR"
            ))
        elif schema["@context"] != "https://schema.org":
            warnings.append(ValidationError(
                path="/@context",
                code="INVALID_CONTEXT",
                message="@context should be 'https://schema.org'",
                severity="WARNING"
            ))

        if "@type" not in schema:
            errors.append(ValidationError(
                path="",
                code="MISSING_TYPE",
                message="Missing @type field",
                severity="ERROR"
            ))
            return self._format_result(False, errors, warnings, schema)

        schema_type = schema["@type"]

        # 2. Check required fields (from registry)
        if self.registry.has_type(schema_type):
            required = self.registry.get_required_fields(schema_type)
            for field in required:
                if field not in schema:
                    errors.append(ValidationError(
                        path=f"/{field}",
                        code="MISSING_REQUIRED_FIELD",
                        message=f"Missing required field: {field}",
                        severity="ERROR"
                    ))

        # 3. Check field values and types (including nested objects)
        type_errors = self._validate_field_types(schema, schema_type)
        errors.extend(type_errors)

        # 4. Check recommended fields (from registry)
        if self.registry.has_type(schema_type):
            recommended = self.registry.get_recommended_fields(schema_type)
            missing_recommended = [f for f in recommended if f not in schema]
            if missing_recommended:
                # Create individual warnings for each missing recommended field
                for field in missing_recommended[:5]:  # Limit to 5 to avoid spam
                    warnings.append(ValidationError(
                        path=f"/{field}",
                        code="MISSING_RECOMMENDED_FIELD",
                        message=f"Missing recommended field: {field}",
                        severity="WARNING"
                    ))

        is_valid = len(errors) == 0

        return self._format_result(is_valid, errors, warnings, schema)

    def _format_result(
        self,
        is_valid: bool,
        errors: List[ValidationError],
        warnings: List[ValidationError],
        schema: Dict[str, Any]
    ) -> Union[Tuple[bool, List[str], List[str]], Dict[str, Any]]:
        """Format validation result based on structured_errors setting."""
        if self.structured_errors:
            return {
                "is_valid": is_valid,
                "errors": [e.to_dict() for e in errors],
                "warnings": [w.to_dict() for w in warnings],
                "completeness_score": self.calculate_completeness_score(schema),
                "suggestions": self.get_optimization_suggestions(schema)
            }
        else:
            # Backward compatibility: return simple string lists
            return (
                is_valid,
                [e.to_string() for e in errors],
                [w.to_string() for w in warnings]
            )

    def _validate_field_types(self, schema: Dict, schema_type: str) -> List[ValidationError]:
        """Validate field types and values, including nested objects."""
        errors: List[ValidationError] = []

        # Article-specific validation
        if schema_type == "Article":
            if "author" in schema:
                author = schema["author"]
                if isinstance(author, dict):
                    if "@type" not in author or author["@type"] != "Person":
                        errors.append(ValidationError(
                            path="/author/@type",
                            code="INVALID_TYPE",
                            message="author should be of type Person",
                            severity="ERROR",
                            context={"expected": "Person", "actual": author.get("@type")}
                        ))
                    if "name" not in author:
                        errors.append(ValidationError(
                            path="/author/name",
                            code="NESTED_MISSING_FIELD",
                            message="author must have a name field",
                            severity="ERROR"
                        ))
                elif not isinstance(author, str):
                    errors.append(ValidationError(
                        path="/author",
                        code="INVALID_VALUE_TYPE",
                        message="author should be a Person object or string",
                        severity="ERROR",
                        context={"expected": "Person or string", "actual": type(author).__name__}
                    ))

            if "datePublished" in schema:
                date = schema["datePublished"]
                if not isinstance(date, str):
                    errors.append(ValidationError(
                        path="/datePublished",
                        code="INVALID_VALUE_TYPE",
                        message="datePublished should be a string (ISO 8601 format)",
                        severity="ERROR",
                        context={"expected": "string", "actual": type(date).__name__}
                    ))

            # Validate publisher (Organization)
            if "publisher" in schema:
                errors.extend(self._validate_nested_organization(schema["publisher"], "/publisher"))

            # Validate image (ImageObject or array)
            if "image" in schema:
                errors.extend(self._validate_nested_image(schema["image"], "/image"))

        # Product-specific validation
        elif schema_type == "Product":
            if "offers" in schema:
                offers = schema["offers"]
                if isinstance(offers, dict):
                    errors.extend(self._validate_nested_offer(offers, "/offers"))
                elif isinstance(offers, list):
                    for i, offer in enumerate(offers):
                        if not isinstance(offer, dict):
                            errors.append(ValidationError(
                                path=f"/offers/{i}",
                                code="INVALID_ARRAY_ITEM",
                                message=f"offers[{i}] should be an Offer object",
                                severity="ERROR"
                            ))
                        else:
                            errors.extend(self._validate_nested_offer(offer, f"/offers/{i}"))

            # Validate aggregateRating
            if "aggregateRating" in schema:
                errors.extend(self._validate_nested_rating(schema["aggregateRating"], "/aggregateRating"))

            # Validate brand
            if "brand" in schema:
                brand = schema["brand"]
                if isinstance(brand, dict) and brand.get("@type") not in ["Brand", "Organization"]:
                    errors.append(ValidationError(
                        path="/brand/@type",
                        code="INVALID_TYPE",
                        message="brand should be of type Brand or Organization",
                        severity="ERROR",
                        context={"expected": "Brand or Organization", "actual": brand.get("@type")}
                    ))

            # Validate image
            if "image" in schema:
                errors.extend(self._validate_nested_image(schema["image"], "/image"))

        # Event-specific validation
        elif schema_type == "Event":
            if "location" in schema:
                location = schema["location"]
                if isinstance(location, dict):
                    if "@type" not in location:
                        errors.append(ValidationError(
                            path="/location/@type",
                            code="NESTED_MISSING_TYPE",
                            message="location should have a @type (Place or VirtualLocation)",
                            severity="ERROR"
                        ))
                    # Validate nested address if present
                    if "address" in location:
                        errors.extend(self._validate_nested_address(location["address"], "/location/address"))

            if "startDate" in schema:
                start_date = schema["startDate"]
                if not isinstance(start_date, str):
                    errors.append(ValidationError(
                        path="/startDate",
                        code="INVALID_VALUE_TYPE",
                        message="startDate should be a string (ISO 8601 format)",
                        severity="ERROR",
                        context={"expected": "string", "actual": type(start_date).__name__}
                    ))

            # Validate organizer
            if "organizer" in schema:
                organizer = schema["organizer"]
                if isinstance(organizer, dict):
                    errors.extend(self._validate_nested_organization(organizer, "/organizer"))

            # Validate image
            if "image" in schema:
                errors.extend(self._validate_nested_image(schema["image"], "/image"))

        # Recipe-specific validation
        elif schema_type == "Recipe":
            if "recipeIngredient" in schema:
                ingredients = schema["recipeIngredient"]
                if not isinstance(ingredients, list):
                    errors.append(ValidationError(
                        path="/recipeIngredient",
                        code="INVALID_VALUE_TYPE",
                        message="recipeIngredient should be a list",
                        severity="ERROR",
                        context={"expected": "list", "actual": type(ingredients).__name__}
                    ))
                elif len(ingredients) == 0:
                    errors.append(ValidationError(
                        path="/recipeIngredient",
                        code="EMPTY_REQUIRED_FIELD",
                        message="recipeIngredient should not be empty",
                        severity="ERROR"
                    ))

            if "recipeInstructions" in schema:
                instructions = schema["recipeInstructions"]
                if isinstance(instructions, list):
                    # Validate HowToStep array
                    errors.extend(self._validate_nested_howto_steps(instructions, "/recipeInstructions"))
                elif not isinstance(instructions, str):
                    errors.append(ValidationError(
                        path="/recipeInstructions",
                        code="INVALID_VALUE_TYPE",
                        message="recipeInstructions should be a list or string",
                        severity="ERROR",
                        context={"expected": "list or string", "actual": type(instructions).__name__}
                    ))

            # Validate nutrition
            if "nutrition" in schema:
                errors.extend(self._validate_nested_nutrition(schema["nutrition"], "/nutrition"))

            # Validate aggregateRating
            if "aggregateRating" in schema:
                errors.extend(self._validate_nested_rating(schema["aggregateRating"], "/aggregateRating"))

            # Validate image
            if "image" in schema:
                errors.extend(self._validate_nested_image(schema["image"], "/image"))

        # FAQPage-specific validation
        elif schema_type == "FAQPage":
            if "mainEntity" in schema:
                entities = schema["mainEntity"]
                if not isinstance(entities, list):
                    errors.append(ValidationError(
                        path="/mainEntity",
                        code="INVALID_VALUE_TYPE",
                        message="mainEntity should be a list of Question objects",
                        severity="ERROR",
                        context={"expected": "list", "actual": type(entities).__name__}
                    ))
                else:
                    for i, entity in enumerate(entities):
                        if not isinstance(entity, dict):
                            errors.append(ValidationError(
                                path=f"/mainEntity/{i}",
                                code="INVALID_ARRAY_ITEM",
                                message=f"mainEntity[{i}] should be a Question object",
                                severity="ERROR"
                            ))
                        elif entity.get("@type") != "Question":
                            errors.append(ValidationError(
                                path=f"/mainEntity/{i}/@type",
                                code="INVALID_TYPE",
                                message=f"mainEntity[{i}] should be of type Question",
                                severity="ERROR",
                                context={"expected": "Question", "actual": entity.get("@type")}
                            ))

        # HowTo-specific validation
        elif schema_type == "HowTo":
            if "step" in schema:
                steps = schema["step"]
                if not isinstance(steps, list):
                    errors.append(ValidationError(
                        path="/step",
                        code="INVALID_VALUE_TYPE",
                        message="step should be a list of HowToStep objects",
                        severity="ERROR",
                        context={"expected": "list", "actual": type(steps).__name__}
                    ))
                elif len(steps) == 0:
                    errors.append(ValidationError(
                        path="/step",
                        code="EMPTY_REQUIRED_FIELD",
                        message="step should not be empty",
                        severity="ERROR"
                    ))
                else:
                    errors.extend(self._validate_nested_howto_steps(steps, "/step"))

        # Course-specific validation
        elif schema_type == "Course":
            if "provider" in schema:
                provider = schema["provider"]
                if isinstance(provider, dict):
                    errors.extend(self._validate_nested_organization(provider, "/provider"))

        # Organization-specific validation
        elif schema_type == "Organization":
            if "address" in schema:
                errors.extend(self._validate_nested_address(schema["address"], "/address"))
            if "logo" in schema:
                errors.extend(self._validate_nested_image(schema["logo"], "/logo"))

        # Person-specific validation
        elif schema_type == "Person":
            if "address" in schema:
                errors.extend(self._validate_nested_address(schema["address"], "/address"))
            if "worksFor" in schema and isinstance(schema["worksFor"], dict):
                errors.extend(self._validate_nested_organization(schema["worksFor"], "/worksFor"))
            if "image" in schema:
                errors.extend(self._validate_nested_image(schema["image"], "/image"))

        return errors

    def get_optimization_suggestions(self, schema: Dict) -> List[str]:
        """
        Get optimization suggestions for improving schema markup.

        Args:
            schema: Schema.org JSON-LD dictionary

        Returns:
            List of suggestion messages
        """
        suggestions = []

        schema_type = schema.get("@type")
        if not schema_type:
            return suggestions

        # Article optimization suggestions
        if schema_type == "Article":
            if "image" not in schema:
                suggestions.append("Add 'image' field to improve search result appearance")
            if "datePublished" not in schema:
                suggestions.append("Add 'datePublished' field for better content freshness signals")
            if "publisher" not in schema:
                suggestions.append("Add 'publisher' field to establish content authority")
            if "description" not in schema:
                suggestions.append("Add 'description' field for better search snippets")

        # Product optimization suggestions
        elif schema_type == "Product":
            if "image" not in schema:
                suggestions.append("Add 'image' field to enable rich product results")
            if "brand" not in schema:
                suggestions.append("Add 'brand' field to improve product visibility")
            if "aggregateRating" not in schema:
                suggestions.append("Add 'aggregateRating' field to display star ratings in search")
            offers = schema.get("offers", {})
            if isinstance(offers, dict):
                if "availability" not in offers:
                    suggestions.append("Add 'availability' to offers for stock status display")
                if "priceCurrency" not in offers:
                    suggestions.append("Add 'priceCurrency' to offers for proper price display")

        # Event optimization suggestions
        elif schema_type == "Event":
            if "image" not in schema:
                suggestions.append("Add 'image' field for visual event listings")
            if "description" not in schema:
                suggestions.append("Add 'description' field for detailed event information")
            if "offers" not in schema:
                suggestions.append("Add 'offers' field if event has ticketing")
            if "organizer" not in schema:
                suggestions.append("Add 'organizer' field to show event host")

        # Recipe optimization suggestions
        elif schema_type == "Recipe":
            if "image" not in schema:
                suggestions.append("Add 'image' field for visual recipe cards")
            if "aggregateRating" not in schema:
                suggestions.append("Add 'aggregateRating' field to display recipe ratings")
            if "prepTime" not in schema or "cookTime" not in schema:
                suggestions.append("Add 'prepTime' and 'cookTime' fields for time estimates")
            if "nutrition" not in schema:
                suggestions.append("Add 'nutrition' field for nutritional information")

        # General suggestions
        if "url" not in schema:
            suggestions.append("Add 'url' field to link to the canonical page")

        return suggestions

    def calculate_completeness_score(self, schema: Dict) -> float:
        """
        Calculate schema completeness score (0-100).

        Score is based on:
        - Required fields present: 50%
        - Recommended fields filled: 50%

        Args:
            schema: Schema.org JSON-LD dictionary

        Returns:
            Completeness score from 0.0 to 100.0
        """
        if "@type" not in schema:
            return 0.0

        schema_type = schema.get("@type")
        
        # Unknown types get full score
        if not self.registry.has_type(schema_type):
            return 100.0

        required_fields = self.registry.get_required_fields(schema_type)
        recommended_fields = self.registry.get_recommended_fields(schema_type)

        # Calculate required fields score (50%)
        required_present = sum(1 for field in required_fields if field in schema)
        required_score = (required_present / len(required_fields) * 50) if required_fields else 50

        # Calculate recommended fields score (50%)
        recommended_present = sum(1 for field in recommended_fields if field in schema)
        recommended_score = (recommended_present / len(recommended_fields) * 50) if recommended_fields else 0

        return round(required_score + recommended_score, 2)

    # ========== Nested Object Validation Methods ==========

    def _validate_nested_offer(self, offer: Dict[str, Any], path: str) -> List[ValidationError]:
        """Validate Offer nested object."""
        errors: List[ValidationError] = []

        if not isinstance(offer, dict):
            errors.append(ValidationError(
                path=path,
                code="INVALID_VALUE_TYPE",
                message="Offer must be an object",
                severity="ERROR",
                context={"expected": "object", "actual": type(offer).__name__}
            ))
            return errors

        # Check @type
        if "@type" not in offer or offer["@type"] != "Offer":
            errors.append(ValidationError(
                path=f"{path}/@type",
                code="NESTED_INVALID_TYPE",
                message="offers must be of type Offer",
                severity="ERROR",
                context={"expected": "Offer", "actual": offer.get("@type")}
            ))

        # Check required fields
        if "price" not in offer and "priceSpecification" not in offer:
            errors.append(ValidationError(
                path=f"{path}/price",
                code="NESTED_MISSING_FIELD",
                message="offers must have price or priceSpecification",
                severity="ERROR"
            ))

        return errors

    def _validate_nested_address(self, address: Any, path: str) -> List[ValidationError]:
        """Validate PostalAddress nested object."""
        errors: List[ValidationError] = []

        if isinstance(address, str):
            # String address is acceptable
            return errors

        if not isinstance(address, dict):
            errors.append(ValidationError(
                path=path,
                code="INVALID_VALUE_TYPE",
                message="address must be a PostalAddress object or string",
                severity="ERROR",
                context={"expected": "PostalAddress or string", "actual": type(address).__name__}
            ))
            return errors

        # Check @type
        if "@type" in address and address["@type"] != "PostalAddress":
            errors.append(ValidationError(
                path=f"{path}/@type",
                code="NESTED_INVALID_TYPE",
                message="address must be of type PostalAddress",
                severity="ERROR",
                context={"expected": "PostalAddress", "actual": address.get("@type")}
            ))

        return errors

    def _validate_nested_rating(self, rating: Dict[str, Any], path: str) -> List[ValidationError]:
        """Validate AggregateRating nested object."""
        errors: List[ValidationError] = []

        if not isinstance(rating, dict):
            errors.append(ValidationError(
                path=path,
                code="INVALID_VALUE_TYPE",
                message="aggregateRating must be an object",
                severity="ERROR",
                context={"expected": "object", "actual": type(rating).__name__}
            ))
            return errors

        # Check @type
        if "@type" not in rating or rating["@type"] != "AggregateRating":
            errors.append(ValidationError(
                path=f"{path}/@type",
                code="NESTED_INVALID_TYPE",
                message="aggregateRating must be of type AggregateRating",
                severity="ERROR",
                context={"expected": "AggregateRating", "actual": rating.get("@type")}
            ))

        # Check required fields
        if "ratingValue" not in rating:
            errors.append(ValidationError(
                path=f"{path}/ratingValue",
                code="NESTED_MISSING_FIELD",
                message="aggregateRating must have ratingValue",
                severity="ERROR"
            ))
        elif not isinstance(rating["ratingValue"], (int, float)):
            errors.append(ValidationError(
                path=f"{path}/ratingValue",
                code="INVALID_VALUE_TYPE",
                message="ratingValue must be a number",
                severity="ERROR",
                context={"expected": "number", "actual": type(rating["ratingValue"]).__name__}
            ))

        if "reviewCount" not in rating:
            errors.append(ValidationError(
                path=f"{path}/reviewCount",
                code="NESTED_MISSING_FIELD",
                message="aggregateRating must have reviewCount",
                severity="ERROR"
            ))

        return errors

    def _validate_nested_image(self, image: Any, path: str) -> List[ValidationError]:
        """Validate ImageObject or array of ImageObjects."""
        errors: List[ValidationError] = []

        if isinstance(image, str):
            # String URL is acceptable
            return errors
        elif isinstance(image, list):
            # Array of images
            for i, img in enumerate(image):
                if isinstance(img, dict):
                    if "@type" in img and img["@type"] != "ImageObject":
                        errors.append(ValidationError(
                            path=f"{path}/{i}/@type",
                            code="NESTED_INVALID_TYPE",
                            message=f"image[{i}] must be of type ImageObject",
                            severity="ERROR",
                            context={"expected": "ImageObject", "actual": img.get("@type")}
                        ))
                    if "url" not in img:
                        errors.append(ValidationError(
                            path=f"{path}/{i}/url",
                            code="NESTED_MISSING_FIELD",
                            message=f"image[{i}] must have url",
                            severity="ERROR"
                        ))
        elif isinstance(image, dict):
            # Single ImageObject
            if "@type" in image and image["@type"] != "ImageObject":
                errors.append(ValidationError(
                    path=f"{path}/@type",
                    code="NESTED_INVALID_TYPE",
                    message="image must be of type ImageObject",
                    severity="ERROR",
                    context={"expected": "ImageObject", "actual": image.get("@type")}
                ))
            if "url" not in image:
                errors.append(ValidationError(
                    path=f"{path}/url",
                    code="NESTED_MISSING_FIELD",
                    message="image must have url",
                    severity="ERROR"
                ))

        return errors

    def _validate_nested_howto_steps(self, steps: List[Any], path: str) -> List[ValidationError]:
        """Validate array of HowToStep objects."""
        errors: List[ValidationError] = []

        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(ValidationError(
                    path=f"{path}/{i}",
                    code="INVALID_ARRAY_ITEM",
                    message=f"step[{i}] must be a HowToStep object",
                    severity="ERROR"
                ))
                continue

            # Check @type
            if "@type" in step and step["@type"] != "HowToStep":
                errors.append(ValidationError(
                    path=f"{path}/{i}/@type",
                    code="NESTED_INVALID_TYPE",
                    message=f"step[{i}] must be of type HowToStep",
                    severity="ERROR",
                    context={"expected": "HowToStep", "actual": step.get("@type")}
                ))

            # Check required field
            if "text" not in step:
                errors.append(ValidationError(
                    path=f"{path}/{i}/text",
                    code="NESTED_MISSING_FIELD",
                    message=f"step[{i}] must have text",
                    severity="ERROR"
                ))

        return errors

    def _validate_nested_nutrition(self, nutrition: Dict[str, Any], path: str) -> List[ValidationError]:
        """Validate NutritionInformation nested object."""
        errors: List[ValidationError] = []

        if not isinstance(nutrition, dict):
            errors.append(ValidationError(
                path=path,
                code="INVALID_VALUE_TYPE",
                message="nutrition must be a NutritionInformation object",
                severity="ERROR",
                context={"expected": "object", "actual": type(nutrition).__name__}
            ))
            return errors

        # Check @type
        if "@type" in nutrition and nutrition["@type"] != "NutritionInformation":
            errors.append(ValidationError(
                path=f"{path}/@type",
                code="NESTED_INVALID_TYPE",
                message="nutrition must be of type NutritionInformation",
                severity="ERROR",
                context={"expected": "NutritionInformation", "actual": nutrition.get("@type")}
            ))

        return errors

    def _validate_nested_organization(self, org: Any, path: str) -> List[ValidationError]:
        """Validate Organization nested object."""
        errors: List[ValidationError] = []

        if isinstance(org, str):
            # String name is acceptable
            return errors

        if not isinstance(org, dict):
            errors.append(ValidationError(
                path=path,
                code="INVALID_VALUE_TYPE",
                message="Organization must be an object or string",
                severity="ERROR",
                context={"expected": "Organization or string", "actual": type(org).__name__}
            ))
            return errors

        # Check @type
        if "@type" in org and org["@type"] != "Organization":
            errors.append(ValidationError(
                path=f"{path}/@type",
                code="NESTED_INVALID_TYPE",
                message="Must be of type Organization",
                severity="ERROR",
                context={"expected": "Organization", "actual": org.get("@type")}
            ))

        # Check required field
        if "name" not in org:
            errors.append(ValidationError(
                path=f"{path}/name",
                code="NESTED_MISSING_FIELD",
                message="Organization must have name",
                severity="ERROR"
            ))

        # Validate nested logo if present
        if "logo" in org:
            errors.extend(self._validate_nested_image(org["logo"], f"{path}/logo"))

        return errors

