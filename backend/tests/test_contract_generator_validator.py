import pytest

from backend.services.schema_generator import SchemaGenerator
from backend.services.schema_validator import SchemaValidator


class TestGeneratorValidatorContract:
    def setup_method(self):
        self.generator = SchemaGenerator()
        self.validator = SchemaValidator()

    def test_product_minimal_contract(self):
        content = "Awesome Product\nThis is a product description."
        # Minimal input: rely on generator defaults from content lines
        schema = self.generator.generate("Product", content)

        is_valid, errors, warnings = self.validator.validate(schema)

        assert is_valid is True, f"Expected valid schema, got errors: {errors}"
        assert errors == []
        # Offers should now be recommended (not required); expect a warning mentioning offers
        assert any("offers" in w for w in warnings), f"Expected offers warning, got: {warnings}"

    def test_article_minimal_contract(self):
        content = "An Article Title\nBody of the article"
        schema = self.generator.generate("Article", content)

        is_valid, errors, warnings = self.validator.validate(schema)
        assert is_valid is True, f"Article should be valid, got errors: {errors}"
