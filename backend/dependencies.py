from fastapi import Depends

from backend.registry.schema_registry import SCHEMA_REGISTRY, SchemaRegistry
from backend.services.schema_generator import SchemaGenerator
from backend.services.schema_validator import SchemaValidator


def get_schema_registry() -> SchemaRegistry:
    # Centralized singleton for registry; safe to share across requests
    return SCHEMA_REGISTRY


def get_schema_generator() -> SchemaGenerator:
    # Generator is stateless; new instance is fine for now
    return SchemaGenerator()


def get_schema_validator(
    registry: SchemaRegistry = Depends(get_schema_registry),
) -> SchemaValidator:
    # Validator reads rules from SchemaRegistry
    return SchemaValidator(registry=registry)

