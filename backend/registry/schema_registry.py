from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class SchemaTypeMeta:
    """Metadata for a Schema.org type.

    - template_required/optional: from generator templates (do not include @context/@type)
    - validator_required: required fields used by validator (includes @context/@type)
    - validator_recommended: recommended fields used by validator
    - nested_rules: reserved for future nested validation/generation rules
    """
    template_required: List[str]
    template_optional: List[str]
    validator_required: List[str]
    validator_recommended: List[str]
    nested_rules: Dict[str, Any] = field(default_factory=dict)


class SchemaRegistry:
    """Central registry for schema type metadata (single source of truth).

    NOTE: In this phase we only define and populate the registry. Existing
    generator/validator logic remains unchanged for backward compatibility.
    """

    def __init__(self) -> None:
        self._types: Dict[str, SchemaTypeMeta] = {}

    # ---- Registration / Query API ----
    def register_type(
        self,
        schema_type: str,
        *,
        template_required: List[str],
        template_optional: List[str],
        validator_required: List[str],
        validator_recommended: List[str],
        nested_rules: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not schema_type or not isinstance(schema_type, str):
            raise ValueError("schema_type must be a non-empty string")
        meta = SchemaTypeMeta(
            template_required=list(template_required),
            template_optional=list(template_optional),
            validator_required=list(validator_required),
            validator_recommended=list(validator_recommended),
            nested_rules=dict(nested_rules or {}),
        )
        self._types[schema_type] = meta

    def has_type(self, schema_type: str) -> bool:
        return schema_type in self._types

    def list_types(self) -> List[str]:
        return sorted(self._types.keys())

    def get_template(self, schema_type: str) -> Dict[str, List[str]]:
        if schema_type not in self._types:
            raise ValueError(f"Unknown schema type: {schema_type}")
        m = self._types[schema_type]
        return {"required": list(m.template_required), "optional": list(m.template_optional)}

    def get_required_fields(self, schema_type: str) -> List[str]:
        if schema_type not in self._types:
            raise ValueError(f"Unknown schema type: {schema_type}")
        return list(self._types[schema_type].validator_required)

    def get_recommended_fields(self, schema_type: str) -> List[str]:
        if schema_type not in self._types:
            raise ValueError(f"Unknown schema type: {schema_type}")
        return list(self._types[schema_type].validator_recommended)

    def get_meta(self, schema_type: str) -> SchemaTypeMeta:
        if schema_type not in self._types:
            raise ValueError(f"Unknown schema type: {schema_type}")
        return self._types[schema_type]


# ---- Default registry pre-populated with current project metadata ----
SCHEMA_REGISTRY = SchemaRegistry()

# Templates (from SchemaGenerator.SCHEMA_TEMPLATES)
_templates: Dict[str, Dict[str, List[str]]] = {
    "Article": {
        "required": ["headline", "author"],
        "optional": [
            "description", "image", "publisher", "dateModified", "articleBody", "datePublished"
        ],
    },
    "Product": {
        "required": ["name", "description"],
        "optional": ["brand", "offers", "image", "review", "aggregateRating", "sku"],
    },
    "Organization": {
        "required": ["name"],
        "optional": ["url", "logo", "description", "address", "contactPoint"],
    },
    "Event": {
        "required": ["name", "startDate", "location"],
        "optional": [
            "endDate", "description", "image", "organizer", "performer", "offers", "eventStatus", "eventAttendanceMode"
        ],
    },
    "Person": {
        "required": ["name"],
        "optional": [
            "jobTitle", "worksFor", "url", "image", "sameAs", "alumniOf", "birthDate", "email", "telephone", "address"
        ],
    },
    "Recipe": {
        "required": ["name", "recipeIngredient", "recipeInstructions"],
        "optional": [
            "image", "author", "datePublished", "description", "prepTime", "cookTime", "totalTime", "recipeYield",
            "recipeCategory", "recipeCuisine", "nutrition", "aggregateRating", "keywords"
        ],
    },
    "FAQPage": {
        "required": ["mainEntity"],
        "optional": ["about", "description", "name"],
    },
    "HowTo": {
        "required": ["name", "step"],
        "optional": ["description", "image", "totalTime", "estimatedCost", "supply", "tool", "video"],
    },
    "Course": {
        "required": ["name", "description", "provider"],
        "optional": [
            "url", "courseCode", "hasCourseInstance", "offers", "aggregateRating", "review", "educationalLevel", "timeRequired", "inLanguage"
        ],
    },
}

# Validator fields (from SchemaValidator.REQUIRED_FIELDS / RECOMMENDED_FIELDS)
_required: Dict[str, List[str]] = {
    "Article": ["@context", "@type", "headline", "author"],
    "Product": ["@context", "@type", "name"],
    "Organization": ["@context", "@type", "name"],
    "Event": ["@context", "@type", "name", "startDate", "location"],
    "Person": ["@context", "@type", "name"],
    "Recipe": ["@context", "@type", "name", "recipeIngredient", "recipeInstructions"],
    "FAQPage": ["@context", "@type", "mainEntity"],
    "HowTo": ["@context", "@type", "name", "step"],
    "Course": ["@context", "@type", "name", "description", "provider"],
}

_recommended: Dict[str, List[str]] = {
    "Article": ["image", "datePublished", "publisher", "description"],
    "Product": ["image", "brand", "offers", "aggregateRating", "review"],
    "Organization": ["url", "logo", "description"],
    "Event": ["image", "description", "offers", "organizer"],
    "Person": ["url", "image", "jobTitle"],
    "Recipe": ["image", "author", "prepTime", "cookTime", "aggregateRating"],
    "FAQPage": ["description", "name"],
    "HowTo": ["image", "description", "totalTime"],
    "Course": ["url", "offers", "aggregateRating"],
}

# Populate default registry
for _t, _tpl in _templates.items():
    SCHEMA_REGISTRY.register_type(
        _t,
        template_required=_tpl.get("required", []),
        template_optional=_tpl.get("optional", []),
        validator_required=_required[_t],
        validator_recommended=_recommended[_t],
        nested_rules={},
    )

