"""
Tests for Schema Generator
"""

import pytest
from backend.services.schema_generator import SchemaGenerator


@pytest.fixture
def generator():
    """Create schema generator instance"""
    return SchemaGenerator()


class TestSchemaGenerator:
    """Test schema generation functionality"""

    def test_supported_types(self, generator):
        """Test that all 9 types are supported"""
        types = generator.get_supported_types()
        assert len(types) == 9
        assert "Article" in types
        assert "Product" in types
        assert "Recipe" in types

    def test_generate_article(self, generator):
        """Test Article schema generation"""
        content = "Test Article Title\n\nThis is the article content."
        schema = generator.generate("Article", content, url="https://example.com/article")

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Article"
        assert "headline" in schema
        assert "author" in schema
        assert schema["url"] == "https://example.com/article"

    def test_generate_article_with_metadata(self, generator):
        """Test Article with custom metadata"""
        content = "Custom Article\n\nContent here."
        schema = generator.generate(
            "Article",
            content,
            author="John Doe",
            datePublished="2024-01-15",
            description="Test description"
        )

        assert schema["author"]["name"] == "John Doe"
        assert schema["datePublished"] == "2024-01-15"
        assert schema["description"] == "Test description"

    def test_generate_product(self, generator):
        """Test Product schema generation"""
        content = "Amazing Product\n\nBest product ever."
        schema = generator.generate("Product", content)

        assert schema["@type"] == "Product"
        assert "name" in schema
        assert "description" in schema

    def test_generate_recipe(self, generator):
        """Test Recipe schema generation"""
        content = "Chocolate Cake\n\nDelicious cake recipe."
        schema = generator.generate(
            "Recipe",
            content,
            recipeIngredient=["flour", "sugar", "cocoa"],
            recipeInstructions=["Mix ingredients", "Bake at 350F"]
        )

        assert schema["@type"] == "Recipe"
        assert schema["recipeIngredient"] == ["flour", "sugar", "cocoa"]
        assert len(schema["recipeInstructions"]) == 2

    def test_generate_event(self, generator):
        """Test Event schema generation"""
        content = "Tech Conference 2024\n\nAnnual tech conference."
        schema = generator.generate(
            "Event",
            content,
            startDate="2024-06-15T09:00:00",
            location={"@type": "Place", "name": "Convention Center"}
        )

        assert schema["@type"] == "Event"
        assert schema["startDate"] == "2024-06-15T09:00:00"
        assert schema["location"]["@type"] == "Place"

    def test_generate_faq(self, generator):
        """Test FAQPage schema generation"""
        content = """
        What is Schema.org?
        Schema.org is a structured data vocabulary.
        
        How do I use it?
        Add JSON-LD to your HTML.
        """
        schema = generator.generate("FAQPage", content)

        assert schema["@type"] == "FAQPage"
        assert "mainEntity" in schema
        assert len(schema["mainEntity"]) >= 1
        assert schema["mainEntity"][0]["@type"] == "Question"

    def test_generate_howto(self, generator):
        """Test HowTo schema generation"""
        content = """
        How to Bake Bread
        1. Mix flour and water
        2. Knead the dough
        3. Let it rise
        4. Bake at 400F
        """
        schema = generator.generate("HowTo", content)

        assert schema["@type"] == "HowTo"
        assert "step" in schema
        assert len(schema["step"]) >= 3
        assert schema["step"][0]["@type"] == "HowToStep"

    def test_generate_person(self, generator):
        """Test Person schema generation"""
        content = "John Doe\n\nSoftware Engineer"
        schema = generator.generate(
            "Person",
            content,
            jobTitle="Software Engineer",
            worksFor={"@type": "Organization", "name": "Tech Corp"}
        )

        assert schema["@type"] == "Person"
        assert schema["jobTitle"] == "Software Engineer"
        assert schema["worksFor"]["name"] == "Tech Corp"

    def test_generate_organization(self, generator):
        """Test Organization schema generation"""
        content = "Tech Corp\n\nLeading technology company."
        schema = generator.generate(
            "Organization",
            content,
            url="https://techcorp.com",
            logo="https://techcorp.com/logo.png"
        )

        assert schema["@type"] == "Organization"
        assert schema["url"] == "https://techcorp.com"
        # Logo is now structured as ImageObject
        assert schema["logo"]["@type"] == "ImageObject"
        assert schema["logo"]["url"] == "https://techcorp.com/logo.png"

    def test_generate_course(self, generator):
        """Test Course schema generation"""
        content = "Python Programming\n\nLearn Python from scratch."
        schema = generator.generate(
            "Course",
            content,
            provider={"@type": "Organization", "name": "Code Academy"}
        )

        assert schema["@type"] == "Course"
        assert schema["provider"]["name"] == "Code Academy"

    def test_validate_schema_valid(self, generator):
        """Test validation of valid schema"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test",
            "author": {"@type": "Person", "name": "John"}
        }

        assert generator.validate_schema(schema) is True

    def test_validate_schema_missing_context(self, generator):
        """Test validation fails without @context"""
        schema = {
            "@type": "Article",
            "headline": "Test"
        }

        assert generator.validate_schema(schema) is False

    def test_validate_schema_missing_required_field(self, generator):
        """Test validation fails without required fields"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test"
            # Missing author
        }

        assert generator.validate_schema(schema) is False

    def test_get_template(self, generator):
        """Test getting schema template"""
        template = generator.get_template("Article")

        assert "required" in template
        assert "optional" in template
        assert "headline" in template["required"]
        assert "author" in template["required"]

    def test_unsupported_type_raises_error(self, generator):
        """Test that unsupported type raises ValueError"""
        with pytest.raises(ValueError, match="Unsupported schema type"):
            generator.generate("UnsupportedType", "content")

    def test_unknown_template_raises_error(self, generator):
        """Test that unknown template raises ValueError"""
        with pytest.raises(ValueError, match="Unknown schema type"):
            generator.get_template("UnknownType")

