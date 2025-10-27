from backend.registry.schema_registry import SchemaRegistry, SCHEMA_REGISTRY
from backend.services.schema_generator import SchemaGenerator
from backend.services.schema_validator import SchemaValidator


def test_registry_lists_all_supported_types_matches_generator_and_validator():
    registry_types = set(SCHEMA_REGISTRY.list_types())

    # generator templates
    gen_types = set(SchemaGenerator.SCHEMA_TEMPLATES.keys())
    # validator required/recommended
    val_required_types = set(SchemaValidator.REQUIRED_FIELDS.keys())
    val_recommended_types = set(SchemaValidator.RECOMMENDED_FIELDS.keys())

    assert registry_types == gen_types == val_required_types == val_recommended_types
    assert len(registry_types) == 9


def test_registry_templates_match_generator():
    for t in SchemaGenerator.SCHEMA_TEMPLATES.keys():
        reg_tpl = SCHEMA_REGISTRY.get_template(t)
        gen_tpl = SchemaGenerator.SCHEMA_TEMPLATES[t]
        assert reg_tpl["required"] == gen_tpl["required"], f"required mismatch for {t}"
        assert reg_tpl["optional"] == gen_tpl["optional"], f"optional mismatch for {t}"


def test_registry_required_and_recommended_match_validator():
    for t in SchemaValidator.REQUIRED_FIELDS.keys():
        reg_required = SCHEMA_REGISTRY.get_required_fields(t)
        reg_recommended = SCHEMA_REGISTRY.get_recommended_fields(t)
        assert reg_required == SchemaValidator.REQUIRED_FIELDS[t], f"required mismatch for {t}"
        assert reg_recommended == SchemaValidator.RECOMMENDED_FIELDS[t], f"recommended mismatch for {t}"


def test_can_register_custom_type_and_query():
    r = SchemaRegistry()
    r.register_type(
        "Custom",
        template_required=["name"],
        template_optional=["description"],
        validator_required=["@context", "@type", "name"],
        validator_recommended=["description"],
    )
    assert r.has_type("Custom")
    assert "Custom" in r.list_types()
    assert r.get_template("Custom")["required"] == ["name"]
    assert r.get_required_fields("Custom") == ["@context", "@type", "name"]

