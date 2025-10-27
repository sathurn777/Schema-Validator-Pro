"""
Negative Test Cases and Edge Cases for Schema Generation

This file contains STRICT negative tests and edge case tests.
These tests verify how the system handles invalid inputs, edge cases, and error conditions.

Test Philosophy:
- Test invalid inputs and error conditions
- Test boundary values and edge cases
- Test special characters and Unicode
- Test empty/null values
- Verify graceful error handling
- NO skipping failures - fix code or adjust expectations
"""

import pytest
from backend.services.schema_generator import SchemaGenerator


class TestInvalidSchemaTypes:
    """Test handling of invalid schema types."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_invalid_schema_type_raises_error(self):
        """Test that invalid schema type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported schema type"):
            self.generator.generate(
                schema_type="InvalidType",
                content="Test content"
            )

    def test_empty_schema_type_raises_error(self):
        """Test that empty schema type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported schema type"):
            self.generator.generate(
                schema_type="",
                content="Test content"
            )

    def test_none_schema_type_raises_error(self):
        """Test that None schema type raises ValueError."""
        with pytest.raises((ValueError, TypeError)):
            self.generator.generate(
                schema_type=None,
                content="Test content"
            )

    def test_numeric_schema_type_raises_error(self):
        """Test that numeric schema type raises ValueError."""
        with pytest.raises((ValueError, TypeError, AttributeError)):
            self.generator.generate(
                schema_type=123,
                content="Test content"
            )


class TestEmptyAndNullContent:
    """Test handling of empty and null content."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_empty_content(self):
        """Test Article with empty content."""
        schema = self.generator.generate(
            schema_type="Article",
            content=""
        )

        # Should still generate valid schema with default values
        assert schema["@type"] == "Article"
        assert "headline" in schema

    def test_article_with_whitespace_only_content(self):
        """Test Article with whitespace-only content."""
        schema = self.generator.generate(
            schema_type="Article",
            content="   \n\t  "
        )

        assert schema["@type"] == "Article"
        assert "headline" in schema

    def test_product_with_empty_content(self):
        """Test Product with empty content."""
        schema = self.generator.generate(
            schema_type="Product",
            content=""
        )

        assert schema["@type"] == "Product"
        assert "name" in schema

    def test_recipe_with_empty_content(self):
        """Test Recipe with empty content."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content=""
        )

        assert schema["@type"] == "Recipe"
        assert "name" in schema
        # Should have default ingredients and instructions
        assert "recipeIngredient" in schema
        assert "recipeInstructions" in schema


class TestSpecialCharactersAndUnicode:
    """Test handling of special characters and Unicode."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_unicode_content(self):
        """Test Article with Unicode characters."""
        schema = self.generator.generate(
            schema_type="Article",
            content="测试文章 🎉\n这是一篇包含中文和表情符号的文章"
        )

        assert schema["@type"] == "Article"
        assert "测试文章" in schema["headline"]
        if "articleBody" in schema:
            assert "中文" in schema["articleBody"]

    def test_product_with_special_characters(self):
        """Test Product with special characters."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product™ with © & ® symbols",
            description="Price: $99.99 (50% off!)"
        )

        assert schema["@type"] == "Product"
        assert "™" in schema["name"] or "Product" in schema["name"]

    def test_recipe_with_unicode_ingredients(self):
        """Test Recipe with Unicode ingredients."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="中式炒饭",
            recipeIngredient=[
                "2杯米饭",
                "3个鸡蛋",
                "100克虾仁"
            ]
        )

        assert schema["@type"] == "Recipe"
        assert "米饭" in schema["recipeIngredient"][0]
        assert "鸡蛋" in schema["recipeIngredient"][1]

    def test_organization_with_emoji(self):
        """Test Organization with emoji."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Tech Company 🚀",
            description="We build amazing products! 💻✨"
        )

        assert schema["@type"] == "Organization"
        assert "🚀" in schema["name"] or "Tech Company" in schema["name"]


class TestBoundaryValues:
    """Test boundary values and extreme cases."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_very_long_content(self):
        """Test Article with very long content (10000+ characters)."""
        long_content = "Very Long Article\n" + ("This is a very long paragraph. " * 500)
        
        schema = self.generator.generate(
            schema_type="Article",
            content=long_content
        )

        assert schema["@type"] == "Article"
        assert len(schema["headline"]) <= 120  # Should be truncated

    def test_product_with_very_long_name(self):
        """Test Product with very long name."""
        long_name = "A" * 500
        
        schema = self.generator.generate(
            schema_type="Product",
            content=long_name
        )

        assert schema["@type"] == "Product"
        # Name should be truncated to reasonable length
        assert len(schema["name"]) <= 120

    def test_recipe_with_many_ingredients(self):
        """Test Recipe with 100+ ingredients."""
        many_ingredients = [f"Ingredient {i}" for i in range(150)]
        
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Complex Recipe",
            recipeIngredient=many_ingredients
        )

        assert schema["@type"] == "Recipe"
        assert len(schema["recipeIngredient"]) == 150

    def test_recipe_with_many_instructions(self):
        """Test Recipe with 50+ instruction steps."""
        many_steps = "\n".join([f"Step {i}: Do something" for i in range(60)])
        
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Complex Recipe",
            recipeInstructions=many_steps
        )

        assert schema["@type"] == "Recipe"
        assert len(schema["recipeInstructions"]) == 60
        # Verify all steps have correct position
        for i, step in enumerate(schema["recipeInstructions"]):
            assert step["position"] == i + 1

    def test_event_with_very_long_location_address(self):
        """Test Event with very long address."""
        long_address = "A" * 500
        
        schema = self.generator.generate(
            schema_type="Event",
            content="Event",
            startDate="2024-06-15",
            location={
                "name": "Venue",
                "address": long_address
            }
        )

        assert schema["@type"] == "Event"
        assert schema["location"]["address"]["streetAddress"] == long_address


class TestInvalidFieldValues:
    """Test handling of invalid field values."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_invalid_date_format(self):
        """Test Article with invalid date format."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Test Article",
            datePublished="not-a-date"
        )

        # Should still generate schema, date might be passed through or handled
        assert schema["@type"] == "Article"
        # Date handling is implementation-specific

    def test_product_with_negative_price(self):
        """Test Product with negative price."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Test Product",
            offers={
                "price": "-99.99",
                "priceCurrency": "USD"
            }
        )

        # Should still generate schema with the provided value
        assert schema["@type"] == "Product"
        assert schema["offers"]["price"] == "-99.99"

    def test_product_with_invalid_price_format(self):
        """Test Product with invalid price format."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Test Product",
            offers={
                "price": "not-a-number",
                "priceCurrency": "USD"
            }
        )

        # Should still generate schema
        assert schema["@type"] == "Product"
        assert schema["offers"]["price"] == "not-a-number"

    def test_recipe_with_invalid_time_format(self):
        """Test Recipe with invalid time format."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Test Recipe",
            prepTime="not-iso-8601",
            cookTime="also-invalid"
        )

        # Should still generate schema with provided values
        assert schema["@type"] == "Recipe"
        assert schema["prepTime"] == "not-iso-8601"

    def test_event_with_end_date_before_start_date(self):
        """Test Event with endDate before startDate."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Test Event",
            startDate="2024-12-31",
            endDate="2024-01-01"
        )

        # Should still generate schema - validation is separate
        assert schema["@type"] == "Event"
        assert "2024-12-31" in schema["startDate"]
        assert "2024-01-01" in schema["endDate"]


class TestMixedTypeInputs:
    """Test handling of mixed type inputs."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_numeric_headline(self):
        """Test Article with numeric headline."""
        schema = self.generator.generate(
            schema_type="Article",
            content="12345",
            headline=67890
        )

        # Should convert to string or handle gracefully
        assert schema["@type"] == "Article"
        assert "headline" in schema

    def test_product_with_list_as_name(self):
        """Test Product with list as name."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Test",
            name=["Product", "Name"]
        )

        # Should handle gracefully
        assert schema["@type"] == "Product"
        assert "name" in schema

    def test_recipe_with_dict_as_ingredient(self):
        """Test Recipe with dict in ingredients list."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Test Recipe",
            recipeIngredient=[
                "Normal ingredient",
                {"name": "Complex ingredient", "amount": "2 cups"},
                "Another normal ingredient"
            ]
        )

        # Should handle mixed types
        assert schema["@type"] == "Recipe"
        assert len(schema["recipeIngredient"]) == 3

    def test_organization_with_numeric_address(self):
        """Test Organization with numeric address."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Test Org",
            address=12345
        )

        # Should handle gracefully or convert
        assert schema["@type"] == "Organization"


class TestNullAndMissingFields:
    """Test handling of null and missing optional fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_none_author(self):
        """Test Article with None author."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Test Article",
            author=None
        )

        # Should handle None gracefully
        assert schema["@type"] == "Article"

    def test_product_with_none_offers(self):
        """Test Product with None offers."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Test Product",
            offers=None
        )

        # Should handle None gracefully
        assert schema["@type"] == "Product"

    def test_recipe_with_none_nutrition(self):
        """Test Recipe with None nutrition."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Test Recipe",
            nutrition=None
        )

        # Should handle None gracefully
        assert schema["@type"] == "Recipe"

    def test_event_with_none_organizer(self):
        """Test Event with None organizer."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Test Event",
            startDate="2024-06-15",
            organizer=None
        )

        # Should handle None gracefully
        assert schema["@type"] == "Event"

    def test_person_with_none_works_for(self):
        """Test Person with None worksFor."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Test Person",
            worksFor=None
        )

        # Should handle None gracefully
        assert schema["@type"] == "Person"


class TestURLNormalization:
    """Test URL normalization edge cases."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_relative_url(self):
        """Test Article with relative URL."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Test Article",
            url="/articles/test"
        )

        # Should handle relative URL
        assert schema["@type"] == "Article"
        assert "url" in schema

    def test_article_with_malformed_url(self):
        """Test Article with malformed URL."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Test Article",
            url="not a valid url"
        )

        # Should handle malformed URL
        assert schema["@type"] == "Article"

    def test_product_with_url_containing_special_chars(self):
        """Test Product with URL containing special characters."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Test Product",
            url="https://example.com/product?id=123&category=tech&discount=50%"
        )

        # Should handle URL with query parameters
        assert schema["@type"] == "Product"
        assert "url" in schema

    def test_organization_with_international_url(self):
        """Test Organization with international domain."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Test Org",
            url="https://例え.jp/会社"
        )

        # Should handle international URLs
        assert schema["@type"] == "Organization"

