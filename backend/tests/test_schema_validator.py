"""
Tests for Schema Validator
"""

import pytest
from backend.services.schema_validator import SchemaValidator


@pytest.fixture
def validator():
    """Create schema validator instance"""
    return SchemaValidator()


class TestSchemaValidator:
    """Test schema validation functionality"""

    def test_validate_valid_article(self, validator):
        """Test validation of valid Article schema"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article",
            "author": {"@type": "Person", "name": "John Doe"}
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_context(self, validator):
        """Test validation fails without @context"""
        schema = {
            "@type": "Article",
            "headline": "Test"
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is False
        assert "Missing @context field" in errors

    def test_validate_missing_type(self, validator):
        """Test validation fails without @type"""
        schema = {
            "@context": "https://schema.org",
            "headline": "Test"
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is False
        assert "Missing @type field" in errors

    def test_validate_missing_required_fields(self, validator):
        """Test validation fails without required fields"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test"
            # Missing author
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is False
        assert any("author" in error for error in errors)

    def test_validate_article_author_type(self, validator):
        """Test Article author must be Person type"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Organization", "name": "Company"}  # Wrong type
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is False
        assert any("Person" in error for error in errors)

    def test_validate_product_offers(self, validator):
        """Test Product offers validation"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product",
            "offers": {
                "@type": "Offer"
                # Missing price
            }
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is False
        assert any("price" in error.lower() for error in errors)

    def test_validate_event_location(self, validator):
        """Test Event location validation"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": "Conference",
            "startDate": "2024-06-15",
            "location": {"name": "Convention Center"}  # Missing @type
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is False
        assert any("@type" in error for error in errors)

    def test_validate_recipe_ingredients(self, validator):
        """Test Recipe ingredients must be a list"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Cake",
            "recipeIngredient": "flour, sugar",  # Should be list
            "recipeInstructions": ["Mix", "Bake"]
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is False
        assert any("list" in error for error in errors)

    def test_validate_faq_main_entity(self, validator):
        """Test FAQPage mainEntity must be list of Questions"""
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Answer", "text": "Wrong type"}  # Should be Question
            ]
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is False
        assert any("Question" in error for error in errors)

    def test_validate_howto_steps(self, validator):
        """Test HowTo steps must be a list"""
        schema = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": "Guide",
            "step": "Do this"  # Should be list
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is False
        assert any("list" in error for error in errors)

    def test_warnings_for_missing_recommended_fields(self, validator):
        """Test warnings for missing recommended fields"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"}
            # Missing image, datePublished, publisher, description
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is True
        assert len(warnings) > 0
        assert any("recommended" in warning.lower() for warning in warnings)

    def test_calculate_completeness_score_full(self, validator):
        """Test completeness score for fully complete schema"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"},
            "image": "image.jpg",
            "datePublished": "2024-01-15",
            "publisher": {"@type": "Organization", "name": "Publisher"},
            "description": "Description"
        }

        score = validator.calculate_completeness_score(schema)

        assert score == 100.0

    def test_calculate_completeness_score_partial(self, validator):
        """Test completeness score for partially complete schema"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"}
            # Missing all optional fields
        }

        score = validator.calculate_completeness_score(schema)

        assert score == 50.0  # Only required fields present

    def test_calculate_completeness_score_no_type(self, validator):
        """Test completeness score returns 0 without @type"""
        schema = {
            "@context": "https://schema.org",
            "headline": "Test"
        }

        score = validator.calculate_completeness_score(schema)

        assert score == 0.0

    def test_get_optimization_suggestions_article(self, validator):
        """Test optimization suggestions for Article"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"}
        }

        suggestions = validator.get_optimization_suggestions(schema)

        assert len(suggestions) > 0
        assert any("image" in s.lower() for s in suggestions)
        assert any("datePublished" in s for s in suggestions)

    def test_get_optimization_suggestions_product(self, validator):
        """Test optimization suggestions for Product"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Product",
            "offers": {"@type": "Offer", "price": "99.99"}
        }

        suggestions = validator.get_optimization_suggestions(schema)

        assert len(suggestions) > 0
        assert any("image" in s.lower() for s in suggestions)
        assert any("brand" in s.lower() for s in suggestions)
        assert any("aggregateRating" in s for s in suggestions)

    def test_get_optimization_suggestions_recipe(self, validator):
        """Test optimization suggestions for Recipe"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Recipe",
            "recipeIngredient": ["flour"],
            "recipeInstructions": ["Mix"]
        }

        suggestions = validator.get_optimization_suggestions(schema)

        assert len(suggestions) > 0
        assert any("image" in s.lower() for s in suggestions)
        assert any("prepTime" in s or "cookTime" in s for s in suggestions)

    def test_unknown_schema_type_passes_validation(self, validator):
        """Test that unknown schema types pass validation"""
        schema = {
            "@context": "https://schema.org",
            "@type": "UnknownType",
            "name": "Test"
        }

        is_valid, errors, warnings = validator.validate(schema)

        assert is_valid is True
        assert len(errors) == 0

    def test_unknown_schema_type_full_score(self, validator):
        """Test that unknown schema types get full completeness score"""
        schema = {
            "@context": "https://schema.org",
            "@type": "UnknownType",
            "name": "Test"
        }

        score = validator.calculate_completeness_score(schema)

        assert score == 100.0

