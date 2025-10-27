"""
Strict Product Schema Generation Tests

This file contains STRICT tests for Product schema generation.
These tests verify ACTUAL functionality, not just code coverage.

Test Philosophy:
- Test real business logic, not syntax
- Verify actual values, not just field existence
- Test all parameter combinations
- Test edge cases and error conditions
- NO mocking of core business logic
- NO skipping failures with if statements
"""

import pytest
from backend.services.schema_generator import SchemaGenerator


class TestProductSchemaOffersGeneration:
    """
    CRITICAL: Test Product offers generation.
    
    This is the most important e-commerce functionality.
    Without offers, Product schema is useless for e-commerce.
    """

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_product_with_offers_dict(self):
        """Test Product with offers as dict - CORRECT parameter format."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Wireless Headphones\nPremium audio quality",
            url="https://example.com/product",
            offers={
                "price": "299.99",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            }
        )

        # Strict validation - MUST have offers
        assert "offers" in schema, "Product MUST have offers for e-commerce"
        
        # Validate offers structure
        offers = schema["offers"]
        assert offers["@type"] == "Offer", "offers must be of type Offer"
        assert offers["price"] == "299.99", "price must match input"
        assert offers["priceCurrency"] == "USD", "priceCurrency must match input"
        assert offers["availability"] == "https://schema.org/InStock", "availability must match input"

    def test_product_with_offers_minimal(self):
        """Test Product with minimal offers (only price)."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            offers={"price": "99.99"}
        )

        assert "offers" in schema
        assert schema["offers"]["@type"] == "Offer"
        assert schema["offers"]["price"] == "99.99"
        assert schema["offers"]["priceCurrency"] == "USD"  # Default
        assert schema["offers"]["availability"] == "https://schema.org/InStock"  # Default

    def test_product_with_offers_full(self):
        """Test Product with complete offers information."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            url="https://example.com/product",
            offers={
                "price": "1299.99",
                "priceCurrency": "EUR",
                "availability": "https://schema.org/PreOrder",
                "url": "https://example.com/buy"
            }
        )

        assert "offers" in schema
        offers = schema["offers"]
        assert offers["@type"] == "Offer"
        assert offers["price"] == "1299.99"
        assert offers["priceCurrency"] == "EUR"
        assert offers["availability"] == "https://schema.org/PreOrder"
        assert offers["url"] == "https://example.com/buy"

    def test_product_with_offers_no_url(self):
        """Test Product offers without URL."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            offers={"price": "49.99"}
        )

        assert "offers" in schema
        # URL should not be in offers if not provided
        assert "url" not in schema["offers"] or schema["offers"]["url"] is None

    def test_product_without_offers(self):
        """Test Product without offers - should NOT have offers field."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name"
        )

        # If no offers provided, should not have offers field
        assert "offers" not in schema


class TestProductSchemaSKUAndIdentifiers:
    """Test Product SKU, GTIN, and MPN identifiers."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_product_with_sku(self):
        """Test Product with SKU."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            sku="ABC-123-XYZ"
        )

        assert "sku" in schema, "Product must have SKU when provided"
        assert schema["sku"] == "ABC-123-XYZ", "SKU must match input"

    def test_product_with_gtin13(self):
        """Test Product with GTIN-13."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            gtin13="1234567890123"
        )

        assert "gtin13" in schema, "Product must have gtin13 when provided"
        assert schema["gtin13"] == "1234567890123", "gtin13 must match input"

    def test_product_with_mpn(self):
        """Test Product with MPN."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            mpn="MPN-12345"
        )

        assert "mpn" in schema, "Product must have mpn when provided"
        assert schema["mpn"] == "MPN-12345", "mpn must match input"

    def test_product_with_all_identifiers(self):
        """Test Product with all identifiers."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            sku="SKU-123",
            gtin13="1234567890123",
            mpn="MPN-456"
        )

        assert schema["sku"] == "SKU-123"
        assert schema["gtin13"] == "1234567890123"
        assert schema["mpn"] == "MPN-456"

    def test_product_without_identifiers(self):
        """Test Product without identifiers."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name"
        )

        assert "sku" not in schema
        assert "gtin13" not in schema
        assert "mpn" not in schema


class TestProductSchemaManufacturer:
    """Test Product manufacturer field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_product_with_manufacturer_string(self):
        """Test Product with manufacturer as string."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            manufacturer="TechCorp Inc."
        )

        assert "manufacturer" in schema, "Product must have manufacturer when provided"
        assert schema["manufacturer"]["@type"] == "Organization", "manufacturer must be Organization type"
        assert schema["manufacturer"]["name"] == "TechCorp Inc.", "manufacturer name must match input"

    def test_product_with_manufacturer_dict(self):
        """Test Product with manufacturer as dict."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            manufacturer={
                "name": "TechCorp Inc.",
                "url": "https://techcorp.com"
            }
        )

        assert "manufacturer" in schema
        manufacturer = schema["manufacturer"]
        assert manufacturer["@type"] == "Organization"
        assert manufacturer["name"] == "TechCorp Inc."
        assert manufacturer["url"] == "https://techcorp.com"

    def test_product_without_manufacturer(self):
        """Test Product without manufacturer."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name"
        )

        assert "manufacturer" not in schema


class TestProductSchemaImage:
    """Test Product image field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_product_with_single_image_string(self):
        """Test Product with single image as string."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            url="https://example.com/product",
            image="product.jpg"
        )

        assert "image" in schema, "Product must have image when provided"
        assert isinstance(schema["image"], list), "image must be array"
        assert len(schema["image"]) == 1, "single image should result in array of 1"
        
        image = schema["image"][0]
        assert image["@type"] == "ImageObject", "image must be ImageObject type"
        assert "product.jpg" in image["url"], "image URL must contain filename"

    def test_product_with_multiple_images(self):
        """Test Product with multiple images."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            url="https://example.com/product",
            image=["image1.jpg", "image2.jpg", "image3.jpg"]
        )

        assert "image" in schema
        assert isinstance(schema["image"], list)
        assert len(schema["image"]) == 3, "should have 3 images"
        
        for i, img in enumerate(schema["image"]):
            assert img["@type"] == "ImageObject"
            assert f"image{i+1}.jpg" in img["url"]

    def test_product_with_image_object(self):
        """Test Product with image as ImageObject dict."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            image=[
                {"@type": "ImageObject", "url": "https://example.com/image.jpg", "width": 800, "height": 600}
            ]
        )

        assert "image" in schema
        assert len(schema["image"]) == 1
        
        image = schema["image"][0]
        assert image["@type"] == "ImageObject"
        assert image["url"] == "https://example.com/image.jpg"
        assert image["width"] == 800
        assert image["height"] == 600

    def test_product_without_image(self):
        """Test Product without image."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name"
        )

        assert "image" not in schema


class TestProductSchemaBrand:
    """Test Product brand field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_product_with_brand_string(self):
        """Test Product with brand as string."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            brand_name="Nike"  # Note: code uses _get_default("brand_name")
        )

        assert "brand" in schema, "Product must have brand when provided"
        assert schema["brand"]["@type"] == "Brand", "brand must be Brand type"
        assert schema["brand"]["name"] == "Nike", "brand name must match input"

    def test_product_with_brand_dict(self):
        """Test Product with brand as dict."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            brand_name={"name": "Nike", "url": "https://nike.com"}
        )

        assert "brand" in schema
        brand = schema["brand"]
        assert brand["@type"] == "Brand"
        assert brand["name"] == "Nike"
        assert brand["url"] == "https://nike.com"

    def test_product_without_brand(self):
        """Test Product without brand."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name"
        )

        assert "brand" not in schema


class TestProductSchemaAggregateRating:
    """Test Product aggregateRating field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_product_with_aggregate_rating_dict(self):
        """Test Product with aggregateRating as dict."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            aggregateRating={
                "ratingValue": "4.5",
                "reviewCount": "127"
            }
        )

        assert "aggregateRating" in schema, "Product must have aggregateRating when provided"
        rating = schema["aggregateRating"]
        assert rating["@type"] == "AggregateRating", "aggregateRating must be AggregateRating type"
        assert rating["ratingValue"] == "4.5", "ratingValue must match input"
        assert rating["reviewCount"] == "127", "reviewCount must match input"
        assert rating["bestRating"] == 5, "bestRating should default to 5"
        assert rating["worstRating"] == 1, "worstRating should default to 1"

    def test_product_with_aggregate_rating_full(self):
        """Test Product with complete aggregateRating."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name",
            aggregateRating={
                "ratingValue": "8.5",
                "reviewCount": "1000",
                "bestRating": 10,
                "worstRating": 0
            }
        )

        assert "aggregateRating" in schema
        rating = schema["aggregateRating"]
        assert rating["ratingValue"] == "8.5"
        assert rating["reviewCount"] == "1000"
        assert rating["bestRating"] == 10
        assert rating["worstRating"] == 0

    def test_product_without_aggregate_rating(self):
        """Test Product without aggregateRating."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Product Name"
        )

        assert "aggregateRating" not in schema


class TestProductSchemaComplete:
    """Test complete Product schema with all fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_product_complete_ecommerce(self):
        """Test complete Product schema for e-commerce."""
        schema = self.generator.generate(
            schema_type="Product",
            content="Wireless Noise-Cancelling Headphones\nPremium audio quality with active noise cancellation",
            url="https://example.com/products/headphones-pro",
            name="HeadPhones Pro X",
            description="Professional wireless headphones with industry-leading noise cancellation",
            brand_name="AudioTech",
            sku="HP-PRO-X-001",
            gtin13="1234567890123",
            mpn="HPPROX001",
            manufacturer="AudioTech Manufacturing",
            image=["headphones-front.jpg", "headphones-side.jpg"],
            offers={
                "price": "349.99",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": "https://example.com/buy/headphones-pro"
            },
            aggregateRating={
                "ratingValue": "4.7",
                "reviewCount": "523",
                "bestRating": 5,
                "worstRating": 1
            }
        )

        # Validate all fields
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Product"
        assert schema["name"] == "HeadPhones Pro X"
        assert schema["description"] == "Professional wireless headphones with industry-leading noise cancellation"
        assert schema["url"] == "https://example.com/products/headphones-pro"
        
        # Brand
        assert schema["brand"]["@type"] == "Brand"
        assert schema["brand"]["name"] == "AudioTech"
        
        # Identifiers
        assert schema["sku"] == "HP-PRO-X-001"
        assert schema["gtin13"] == "1234567890123"
        assert schema["mpn"] == "HPPROX001"
        
        # Manufacturer
        assert schema["manufacturer"]["@type"] == "Organization"
        assert schema["manufacturer"]["name"] == "AudioTech Manufacturing"
        
        # Images
        assert len(schema["image"]) == 2
        
        # Offers - CRITICAL
        assert "offers" in schema, "Complete e-commerce product MUST have offers"
        assert schema["offers"]["price"] == "349.99"
        assert schema["offers"]["priceCurrency"] == "USD"
        assert schema["offers"]["availability"] == "https://schema.org/InStock"
        
        # Rating
        assert schema["aggregateRating"]["ratingValue"] == "4.7"
        assert schema["aggregateRating"]["reviewCount"] == "523"

