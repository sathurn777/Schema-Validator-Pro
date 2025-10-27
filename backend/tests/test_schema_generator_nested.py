"""
Tests for Schema Generator - Nested Objects, Normalization, and Site Defaults
"""

import pytest
from datetime import datetime
from backend.services.schema_generator import SchemaGenerator


class TestNestedObjects:
    """Test nested object generation for all schema types"""

    @pytest.fixture
    def generator(self):
        return SchemaGenerator()

    def test_article_publisher_organization(self, generator):
        """Test Article.publisher is structured as Organization with logo"""
        schema = generator.generate(
            "Article",
            "Breaking News: Test Article",
            publisher_name="Tech News Daily",
            publisher_logo="https://example.com/logo.png"
        )
        
        assert "publisher" in schema
        assert schema["publisher"]["@type"] == "Organization"
        assert schema["publisher"]["name"] == "Tech News Daily"
        assert schema["publisher"]["logo"]["@type"] == "ImageObject"
        assert schema["publisher"]["logo"]["url"] == "https://example.com/logo.png"

    def test_article_image_array(self, generator):
        """Test Article.image as array of ImageObjects"""
        schema = generator.generate(
            "Article",
            "Test Article",
            image=["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
        )
        
        assert "image" in schema
        assert isinstance(schema["image"], list)
        assert len(schema["image"]) == 2
        assert schema["image"][0]["@type"] == "ImageObject"
        assert schema["image"][0]["url"] == "https://example.com/img1.jpg"
        assert schema["image"][1]["@type"] == "ImageObject"
        assert schema["image"][1]["url"] == "https://example.com/img2.jpg"

    def test_product_offers_structure(self, generator):
        """Test Product.offers is structured as Offer with price/currency/availability"""
        schema = generator.generate(
            "Product",
            "Amazing Product\nBest product ever",
            offers={
                "price": "99.99",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            }
        )
        
        assert "offers" in schema
        assert schema["offers"]["@type"] == "Offer"
        assert schema["offers"]["price"] == "99.99"
        assert schema["offers"]["priceCurrency"] == "USD"
        assert schema["offers"]["availability"] == "https://schema.org/InStock"

    def test_product_aggregate_rating_structure(self, generator):
        """Test Product.aggregateRating is structured as AggregateRating"""
        schema = generator.generate(
            "Product",
            "Great Product\nHighly rated",
            aggregateRating={
                "ratingValue": 4.5,
                "reviewCount": 120
            }
        )
        
        assert "aggregateRating" in schema
        assert schema["aggregateRating"]["@type"] == "AggregateRating"
        assert schema["aggregateRating"]["ratingValue"] == 4.5
        assert schema["aggregateRating"]["reviewCount"] == 120
        assert schema["aggregateRating"]["bestRating"] == 5
        assert schema["aggregateRating"]["worstRating"] == 1

    def test_product_brand_structure(self, generator):
        """Test Product.brand is structured as Brand"""
        schema = generator.generate(
            "Product",
            "Branded Product\nPremium quality",
            brand_name="Premium Brand"
        )
        
        assert "brand" in schema
        assert schema["brand"]["@type"] == "Brand"
        assert schema["brand"]["name"] == "Premium Brand"

    def test_recipe_instructions_howto_steps(self, generator):
        """Test Recipe.recipeInstructions as HowToStep array"""
        schema = generator.generate(
            "Recipe",
            "Delicious Recipe",
            recipeIngredient=["flour", "sugar", "eggs"],
            recipeInstructions="Mix ingredients\nBake at 350F\nLet cool"
        )
        
        assert "recipeInstructions" in schema
        assert isinstance(schema["recipeInstructions"], list)
        assert len(schema["recipeInstructions"]) == 3
        assert schema["recipeInstructions"][0]["@type"] == "HowToStep"
        assert schema["recipeInstructions"][0]["text"] == "Mix ingredients"
        assert schema["recipeInstructions"][0]["position"] == 1
        assert schema["recipeInstructions"][1]["text"] == "Bake at 350F"
        assert schema["recipeInstructions"][2]["text"] == "Let cool"

    def test_recipe_nutrition_structure(self, generator):
        """Test Recipe.nutrition as NutritionInformation"""
        schema = generator.generate(
            "Recipe",
            "Healthy Recipe",
            recipeIngredient=["vegetables"],
            recipeInstructions="Cook vegetables",
            nutrition={
                "calories": "200 calories",
                "fatContent": "5g",
                "proteinContent": "10g"
            }
        )
        
        assert "nutrition" in schema
        assert schema["nutrition"]["@type"] == "NutritionInformation"
        assert schema["nutrition"]["calories"] == "200 calories"
        assert schema["nutrition"]["fatContent"] == "5g"
        assert schema["nutrition"]["proteinContent"] == "10g"

    def test_event_location_postal_address(self, generator):
        """Test Event.location with PostalAddress"""
        schema = generator.generate(
            "Event",
            "Tech Conference",
            startDate="2025-12-01",
            location={
                "name": "Convention Center",
                "address": {
                    "streetAddress": "123 Main St",
                    "addressLocality": "San Francisco",
                    "addressRegion": "CA",
                    "postalCode": "94102",
                    "addressCountry": "US"
                }
            }
        )
        
        assert "location" in schema
        assert schema["location"]["@type"] == "Place"
        assert schema["location"]["name"] == "Convention Center"
        assert schema["location"]["address"]["@type"] == "PostalAddress"
        assert schema["location"]["address"]["streetAddress"] == "123 Main St"
        assert schema["location"]["address"]["addressLocality"] == "San Francisco"

    def test_event_organizer_structure(self, generator):
        """Test Event.organizer as Organization"""
        schema = generator.generate(
            "Event",
            "Community Meetup",
            startDate="2025-11-15",
            location={"name": "Community Hall"},
            organizer="Tech Community"
        )
        
        assert "organizer" in schema
        assert schema["organizer"]["@type"] == "Organization"
        assert schema["organizer"]["name"] == "Tech Community"

    def test_organization_address_postal(self, generator):
        """Test Organization.address as PostalAddress"""
        schema = generator.generate(
            "Organization",
            "Tech Corp",
            address={
                "streetAddress": "456 Tech Blvd",
                "addressLocality": "Silicon Valley",
                "postalCode": "94000"
            }
        )
        
        assert "address" in schema
        assert schema["address"]["@type"] == "PostalAddress"
        assert schema["address"]["streetAddress"] == "456 Tech Blvd"

    def test_person_works_for_organization(self, generator):
        """Test Person.worksFor as Organization"""
        schema = generator.generate(
            "Person",
            "John Doe",
            worksFor="Tech Corp"
        )
        
        assert "worksFor" in schema
        assert schema["worksFor"]["@type"] == "Organization"
        assert schema["worksFor"]["name"] == "Tech Corp"

    def test_person_address_postal(self, generator):
        """Test Person.address as PostalAddress"""
        schema = generator.generate(
            "Person",
            "Jane Smith",
            address="789 Residential St"
        )
        
        assert "address" in schema
        assert schema["address"]["@type"] == "PostalAddress"
        assert schema["address"]["streetAddress"] == "789 Residential St"


class TestFieldNormalization:
    """Test field normalization (dates, URLs, currency, language)"""

    @pytest.fixture
    def generator(self):
        return SchemaGenerator()

    def test_date_normalization_datetime(self, generator):
        """Test date normalization from datetime object"""
        dt = datetime(2025, 10, 21, 14, 30, 0)
        schema = generator.generate(
            "Article",
            "Test Article",
            datePublished=dt
        )
        
        assert schema["datePublished"] == "2025-10-21T14:30:00"

    def test_date_normalization_string_formats(self, generator):
        """Test date normalization from various string formats"""
        # Test YYYY-MM-DD format
        schema1 = generator.generate("Article", "Test", datePublished="2025-10-21")
        assert schema1["datePublished"] == "2025-10-21"
        
        # Test YYYY/MM/DD format
        schema2 = generator.generate("Article", "Test", datePublished="2025/10/21")
        assert schema2["datePublished"] == "2025-10-21"

    def test_url_normalization_absolute(self, generator):
        """Test URL normalization for absolute URLs"""
        schema = generator.generate(
            "Article",
            "Test Article",
            url="https://example.com/article"
        )
        
        assert schema["url"] == "https://example.com/article"

    def test_currency_normalization_valid(self, generator):
        """Test currency normalization for valid ISO4217 codes"""
        schema = generator.generate(
            "Product",
            "Product\nDescription",
            offers={"price": "99.99", "priceCurrency": "eur"}
        )
        
        assert schema["offers"]["priceCurrency"] == "EUR"

    def test_currency_normalization_invalid_defaults_usd(self, generator):
        """Test currency normalization defaults to USD for invalid codes"""
        schema = generator.generate(
            "Product",
            "Product\nDescription",
            offers={"price": "99.99", "priceCurrency": "INVALID"}
        )
        
        assert schema["offers"]["priceCurrency"] == "USD"


class TestSiteDefaults:
    """Test site-level default configuration"""

    def test_site_defaults_publisher(self):
        """Test site defaults for publisher"""
        generator = SchemaGenerator(site_defaults={
            "publisher_name": "Default Publisher",
            "publisher_logo": "https://default.com/logo.png"
        })
        
        schema = generator.generate("Article", "Test Article")
        
        assert schema["publisher"]["name"] == "Default Publisher"
        assert schema["publisher"]["logo"]["url"] == "https://default.com/logo.png"

    def test_site_defaults_override_with_kwargs(self):
        """Test that kwargs override site defaults"""
        generator = SchemaGenerator(site_defaults={
            "publisher_name": "Default Publisher"
        })
        
        schema = generator.generate(
            "Article",
            "Test Article",
            publisher_name="Override Publisher"
        )
        
        assert schema["publisher"]["name"] == "Override Publisher"

    def test_site_defaults_brand(self):
        """Test site defaults for brand"""
        generator = SchemaGenerator(site_defaults={
            "brand_name": "Default Brand"
        })
        
        schema = generator.generate("Product", "Product\nDescription")
        
        assert schema["brand"]["name"] == "Default Brand"

    def test_no_site_defaults(self):
        """Test generator works without site defaults"""
        generator = SchemaGenerator()
        schema = generator.generate("Article", "Test Article")
        
        # Should not have publisher if not provided
        assert "publisher" not in schema or schema.get("publisher") is None

