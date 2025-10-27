"""
Tests for Schema Validator - Nested Object Validation and Structured Errors
"""

import pytest
from backend.services.schema_validator import SchemaValidator


class TestNestedObjectValidation:
    """Test nested object validation (Offer, Address, Rating, etc.)"""

    @pytest.fixture
    def validator(self):
        """Create validator with default settings (backward compatible)"""
        return SchemaValidator()
    
    @pytest.fixture
    def structured_validator(self):
        """Create validator with structured errors enabled"""
        return SchemaValidator(structured_errors=True)

    # ========== Offer Validation Tests ==========

    def test_product_offers_valid(self, validator):
        """Test valid Product offers passes validation"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product",
            "offers": {
                "@type": "Offer",
                "price": "99.99",
                "priceCurrency": "USD"
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True
        assert len(errors) == 0

    def test_product_offers_missing_type(self, validator):
        """Test Product offers without @type fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product",
            "offers": {
                "price": "99.99"
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("Offer" in error for error in errors)

    def test_product_offers_missing_price(self, validator):
        """Test Product offers without price fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product",
            "offers": {
                "@type": "Offer"
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("price" in error.lower() for error in errors)

    # ========== AggregateRating Validation Tests ==========

    def test_product_rating_valid(self, validator):
        """Test valid AggregateRating passes"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product",
            "offers": {"@type": "Offer", "price": "99.99"},
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": 4.5,
                "reviewCount": 100
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True

    def test_product_rating_missing_type(self, validator):
        """Test AggregateRating without @type fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product",
            "offers": {"@type": "Offer", "price": "99.99"},
            "aggregateRating": {
                "ratingValue": 4.5,
                "reviewCount": 100
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("AggregateRating" in error for error in errors)

    def test_product_rating_missing_value(self, validator):
        """Test AggregateRating without ratingValue fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product",
            "offers": {"@type": "Offer", "price": "99.99"},
            "aggregateRating": {
                "@type": "AggregateRating",
                "reviewCount": 100
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("ratingValue" in error for error in errors)

    def test_product_rating_invalid_value_type(self, validator):
        """Test AggregateRating with non-numeric ratingValue fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test Product",
            "offers": {"@type": "Offer", "price": "99.99"},
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "four point five",  # Should be number
                "reviewCount": 100
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("number" in error.lower() for error in errors)

    # ========== PostalAddress Validation Tests ==========

    def test_organization_address_valid_object(self, validator):
        """Test valid PostalAddress object passes"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Test Org",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "123 Main St",
                "addressLocality": "City"
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True

    def test_organization_address_valid_string(self, validator):
        """Test string address is acceptable"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Test Org",
            "address": "123 Main St, City, State"
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True

    def test_organization_address_invalid_type(self, validator):
        """Test address with wrong @type fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Test Org",
            "address": {
                "@type": "Place",  # Should be PostalAddress
                "streetAddress": "123 Main St"
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("PostalAddress" in error for error in errors)

    # ========== ImageObject Validation Tests ==========

    def test_article_image_valid_string(self, validator):
        """Test string image URL is acceptable"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"},
            "image": "https://example.com/image.jpg"
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True

    def test_article_image_valid_object(self, validator):
        """Test valid ImageObject passes"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"},
            "image": {
                "@type": "ImageObject",
                "url": "https://example.com/image.jpg"
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True

    def test_article_image_valid_array(self, validator):
        """Test array of ImageObjects passes"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"},
            "image": [
                {"@type": "ImageObject", "url": "https://example.com/img1.jpg"},
                {"@type": "ImageObject", "url": "https://example.com/img2.jpg"}
            ]
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True

    def test_article_image_missing_url(self, validator):
        """Test ImageObject without url fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"},
            "image": {
                "@type": "ImageObject"
                # Missing url
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("url" in error.lower() for error in errors)

    def test_article_image_array_invalid_item(self, validator):
        """Test array with invalid ImageObject fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"},
            "image": [
                {"@type": "ImageObject", "url": "https://example.com/img1.jpg"},
                {"@type": "ImageObject"}  # Missing url
            ]
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("url" in error.lower() for error in errors)

    # ========== HowToStep Validation Tests ==========

    def test_recipe_instructions_valid_steps(self, validator):
        """Test valid HowToStep array passes"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Test Recipe",
            "recipeIngredient": ["flour"],
            "recipeInstructions": [
                {"@type": "HowToStep", "text": "Mix ingredients"},
                {"@type": "HowToStep", "text": "Bake"}
            ]
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True

    def test_recipe_instructions_missing_text(self, validator):
        """Test HowToStep without text fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Test Recipe",
            "recipeIngredient": ["flour"],
            "recipeInstructions": [
                {"@type": "HowToStep"}  # Missing text
            ]
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("text" in error.lower() for error in errors)

    def test_recipe_instructions_invalid_type(self, validator):
        """Test HowToStep with wrong @type fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Test Recipe",
            "recipeIngredient": ["flour"],
            "recipeInstructions": [
                {"@type": "Step", "text": "Mix"}  # Wrong type
            ]
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("HowToStep" in error for error in errors)

    # ========== NutritionInformation Validation Tests ==========

    def test_recipe_nutrition_valid(self, validator):
        """Test valid NutritionInformation passes"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Test Recipe",
            "recipeIngredient": ["flour"],
            "recipeInstructions": "Mix",
            "nutrition": {
                "@type": "NutritionInformation",
                "calories": "200 calories"
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True

    def test_recipe_nutrition_invalid_type(self, validator):
        """Test nutrition with wrong @type fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Test Recipe",
            "recipeIngredient": ["flour"],
            "recipeInstructions": "Mix",
            "nutrition": {
                "@type": "Nutrition",  # Wrong type
                "calories": "200 calories"
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("NutritionInformation" in error for error in errors)

    # ========== Organization Validation Tests ==========

    def test_article_publisher_valid(self, validator):
        """Test valid Organization publisher passes"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"},
            "publisher": {
                "@type": "Organization",
                "name": "Publisher"
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is True

    def test_article_publisher_missing_name(self, validator):
        """Test Organization without name fails"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"},
            "publisher": {
                "@type": "Organization"
                # Missing name
            }
        }
        
        is_valid, errors, warnings = validator.validate(schema)
        assert is_valid is False
        assert any("name" in error.lower() for error in errors)


class TestStructuredErrors:
    """Test structured error output with field paths and error codes"""

    @pytest.fixture
    def structured_validator(self):
        """Create validator with structured errors enabled"""
        return SchemaValidator(structured_errors=True)

    def test_structured_error_format(self, structured_validator):
        """Test structured error output format"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test"
            # Missing author
        }

        result = structured_validator.validate(schema)

        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "completeness_score" in result
        assert "suggestions" in result

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0

        # Check error structure
        error = result["errors"][0]
        assert "path" in error
        assert "code" in error
        assert "message" in error
        assert "message_key" in error
        assert "severity" in error

    def test_error_field_path(self, structured_validator):
        """Test error field path is correct"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test",
            "offers": {
                "@type": "Offer"
                # Missing price
            }
        }

        result = structured_validator.validate(schema)

        # Find the price error
        price_errors = [e for e in result["errors"] if "price" in e["path"]]
        assert len(price_errors) > 0
        assert price_errors[0]["path"] == "/offers/price"

    def test_error_code_classification(self, structured_validator):
        """Test error codes are correctly classified"""
        schema = {
            "@type": "Article",  # Missing @context
            "headline": "Test"   # Missing author
        }

        result = structured_validator.validate(schema)

        # Check for MISSING_CONTEXT error
        context_errors = [e for e in result["errors"] if e["code"] == "MISSING_CONTEXT"]
        assert len(context_errors) == 1
        assert context_errors[0]["path"] == ""

        # Check for MISSING_REQUIRED_FIELD error
        required_errors = [e for e in result["errors"] if e["code"] == "MISSING_REQUIRED_FIELD"]
        assert len(required_errors) > 0

    def test_nested_object_error_path(self, structured_validator):
        """Test nested object errors have correct paths"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Test",
            "offers": {
                "@type": "WrongType",  # Should be Offer
                "price": "99.99"
            }
        }

        result = structured_validator.validate(schema)

        # Find the type error
        type_errors = [e for e in result["errors"] if e["code"] == "NESTED_INVALID_TYPE"]
        assert len(type_errors) > 0
        assert type_errors[0]["path"] == "/offers/@type"
        assert "context" in type_errors[0]
        assert type_errors[0]["context"]["expected"] == "Offer"

    def test_array_item_error_path(self, structured_validator):
        """Test array item errors have correct index in path"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"},
            "image": [
                {"@type": "ImageObject", "url": "https://example.com/img1.jpg"},
                {"@type": "ImageObject"}  # Missing url
            ]
        }

        result = structured_validator.validate(schema)

        # Find the url error for second image
        url_errors = [e for e in result["errors"] if "/image/1/url" in e["path"]]
        assert len(url_errors) > 0
        assert url_errors[0]["path"] == "/image/1/url"

    def test_warning_severity(self, structured_validator):
        """Test warnings have correct severity"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"}
            # Missing recommended fields
        }

        result = structured_validator.validate(schema)

        assert result["is_valid"] is True
        assert len(result["warnings"]) > 0

        # Check warning structure
        warning = result["warnings"][0]
        assert warning["severity"] == "WARNING"
        assert warning["code"] == "MISSING_RECOMMENDED_FIELD"

    def test_message_key_format(self, structured_validator):
        """Test message keys follow i18n format"""
        schema = {
            "@type": "Article"  # Missing @context and other fields
        }

        result = structured_validator.validate(schema)

        for error in result["errors"]:
            assert error["message_key"].startswith("error.")
            assert error["message_key"] == f"error.{error['code'].lower()}"

        for warning in result["warnings"]:
            assert warning["message_key"].startswith("warning.")
            assert warning["message_key"] == f"warning.{warning['code'].lower()}"

    def test_completeness_score_included(self, structured_validator):
        """Test completeness score is included in structured output"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"}
        }

        result = structured_validator.validate(schema)

        assert "completeness_score" in result
        assert isinstance(result["completeness_score"], (int, float))
        assert 0 <= result["completeness_score"] <= 100

    def test_suggestions_included(self, structured_validator):
        """Test optimization suggestions are included"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"}
        }

        result = structured_validator.validate(schema)

        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)
        assert len(result["suggestions"]) > 0

    def test_backward_compatibility_default(self):
        """Test default validator maintains backward compatibility"""
        validator = SchemaValidator()  # Default: structured_errors=False

        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test"
        }

        result = validator.validate(schema)

        # Should return tuple, not dict
        assert isinstance(result, tuple)
        assert len(result) == 3
        is_valid, errors, warnings = result
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
        assert isinstance(warnings, list)
        # Errors should be strings
        if len(errors) > 0:
            assert isinstance(errors[0], str)

