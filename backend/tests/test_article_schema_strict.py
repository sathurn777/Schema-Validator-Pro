"""
Strict Article Schema Generation Tests

This file contains STRICT tests for Article schema generation.
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
from datetime import datetime
from backend.services.schema_generator import SchemaGenerator


class TestArticleSchemaArticleBodyGeneration:
    """
    CRITICAL: Test Article articleBody generation.
    
    This is essential for SEO - Article schema MUST have articleBody.
    """

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_multiline_content_generates_article_body(self):
        """Test Article with multi-line content - MUST generate articleBody from content."""
        schema = self.generator.generate(
            schema_type="Article",
            content="How to Build a Website\nThis is a comprehensive guide to building a website. First, you need to choose a domain name. Then, select a hosting provider.",
            url="https://example.com/article"
        )

        # CRITICAL: Article MUST have articleBody for SEO
        assert "articleBody" in schema, "Article MUST have articleBody field"
        
        # Verify articleBody contains the actual content (not just the headline)
        article_body = schema["articleBody"]
        assert "comprehensive guide" in article_body, "articleBody must contain actual content"
        assert "domain name" in article_body, "articleBody must contain full content"
        assert "hosting provider" in article_body, "articleBody must contain full content"
        
        # Headline should be separate from articleBody
        assert schema["headline"] == "How to Build a Website"
        assert "How to Build a Website" not in article_body, "articleBody should not include headline"

    def test_article_with_explicit_article_body(self):
        """Test Article with explicitly provided articleBody."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title",
            url="https://example.com/article",
            articleBody="This is the explicit article body content."
        )

        assert "articleBody" in schema
        assert schema["articleBody"] == "This is the explicit article body content."

    def test_article_with_single_line_content(self):
        """Test Article with single-line content - should still have articleBody."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Single Line Article",
            url="https://example.com/article"
        )

        # Even with single line, should have articleBody (same as content)
        assert "articleBody" in schema
        assert schema["articleBody"] == "Single Line Article"

    def test_article_body_extraction_from_content(self):
        """Test that articleBody is correctly extracted from multi-paragraph content."""
        content = """Breaking News: Major Discovery
Scientists have made a groundbreaking discovery in quantum physics.

The research team at MIT announced today that they have successfully demonstrated quantum entanglement at room temperature.

This breakthrough could revolutionize computing and telecommunications."""

        schema = self.generator.generate(
            schema_type="Article",
            content=content,
            url="https://example.com/news"
        )

        assert "articleBody" in schema
        article_body = schema["articleBody"]
        
        # Should contain all paragraphs except the headline
        assert "Scientists have made" in article_body
        assert "research team at MIT" in article_body
        assert "revolutionize computing" in article_body
        
        # Should NOT contain the headline
        assert "Breaking News: Major Discovery" not in article_body

    def test_article_body_with_empty_lines(self):
        """Test Article with empty lines in content."""
        content = """Article Title

First paragraph.

Second paragraph.

Third paragraph."""

        schema = self.generator.generate(
            schema_type="Article",
            content=content,
            url="https://example.com/article"
        )

        assert "articleBody" in schema
        article_body = schema["articleBody"]
        
        # Should preserve structure
        assert "First paragraph" in article_body
        assert "Second paragraph" in article_body
        assert "Third paragraph" in article_body


class TestArticleSchemaAuthorGeneration:
    """Test Article author field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_author_string(self):
        """Test Article with author as string."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content",
            author="John Doe"
        )

        assert "author" in schema
        assert schema["author"]["@type"] == "Person"
        assert schema["author"]["name"] == "John Doe"

    def test_article_with_author_dict(self):
        """Test Article with author as dict."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content",
            author={
                "name": "Jane Smith",
                "url": "https://example.com/authors/jane"
            }
        )

        assert "author" in schema
        author = schema["author"]
        assert author["@type"] == "Person"
        assert author["name"] == "Jane Smith"
        assert author["url"] == "https://example.com/authors/jane"

    def test_article_without_author_has_default(self):
        """Test Article without author gets default author."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content"
        )

        assert "author" in schema
        assert schema["author"]["@type"] == "Person"
        assert schema["author"]["name"] == "Unknown"


class TestArticleSchemaPublisherGeneration:
    """Test Article publisher field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_publisher_name(self):
        """Test Article with publisher name."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content",
            publisher_name="Tech Blog"
        )

        assert "publisher" in schema
        assert schema["publisher"]["@type"] == "Organization"
        assert schema["publisher"]["name"] == "Tech Blog"

    def test_article_with_publisher_and_logo(self):
        """Test Article with publisher name and logo."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content",
            url="https://example.com/article",
            publisher_name="Tech Blog",
            publisher_logo="logo.png"
        )

        assert "publisher" in schema
        publisher = schema["publisher"]
        assert publisher["@type"] == "Organization"
        assert publisher["name"] == "Tech Blog"
        assert "logo" in publisher
        assert publisher["logo"]["@type"] == "ImageObject"
        assert "logo.png" in publisher["logo"]["url"]

    def test_article_without_publisher(self):
        """Test Article without publisher."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content"
        )

        # Publisher is optional
        assert "publisher" not in schema or schema["publisher"] is not None


class TestArticleSchemaImageGeneration:
    """Test Article image field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_single_image(self):
        """Test Article with single image."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content",
            url="https://example.com/article",
            image="article-image.jpg"
        )

        assert "image" in schema
        assert isinstance(schema["image"], list)
        assert len(schema["image"]) == 1
        
        image = schema["image"][0]
        assert image["@type"] == "ImageObject"
        assert "article-image.jpg" in image["url"]

    def test_article_with_multiple_images(self):
        """Test Article with multiple images."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content",
            url="https://example.com/article",
            image=["image1.jpg", "image2.jpg", "image3.jpg"]
        )

        assert "image" in schema
        assert isinstance(schema["image"], list)
        assert len(schema["image"]) == 3
        
        for i, img in enumerate(schema["image"]):
            assert img["@type"] == "ImageObject"
            assert f"image{i+1}.jpg" in img["url"]

    def test_article_without_image(self):
        """Test Article without image."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content"
        )

        # Image is optional
        assert "image" not in schema


class TestArticleSchemaDateGeneration:
    """Test Article date fields generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_with_date_published(self):
        """Test Article with datePublished."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content",
            datePublished="2024-01-15"
        )

        assert "datePublished" in schema
        # Should be normalized to ISO 8601 format
        assert "2024-01-15" in schema["datePublished"]

    def test_article_with_date_modified(self):
        """Test Article with dateModified."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content",
            datePublished="2024-01-15",
            dateModified="2024-01-20"
        )

        assert "datePublished" in schema
        assert "dateModified" in schema
        assert "2024-01-15" in schema["datePublished"]
        assert "2024-01-20" in schema["dateModified"]

    def test_article_without_date_gets_current_date(self):
        """Test Article without datePublished gets current date."""
        schema = self.generator.generate(
            schema_type="Article",
            content="Article Title\nArticle content"
        )

        assert "datePublished" in schema
        # Should have a valid date
        assert schema["datePublished"] is not None
        assert len(schema["datePublished"]) > 0


class TestArticleSchemaComplete:
    """Test complete Article schema with all fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_article_complete_blog_post(self):
        """Test complete Article schema for a blog post."""
        content = """How to Master Python Programming
Python is one of the most popular programming languages in the world.

In this comprehensive guide, we'll cover everything you need to know to become a Python expert.

From basic syntax to advanced concepts, this article has it all."""

        schema = self.generator.generate(
            schema_type="Article",
            content=content,
            url="https://example.com/blog/python-guide",
            author={
                "name": "John Doe",
                "url": "https://example.com/authors/john"
            },
            datePublished="2024-01-15",
            dateModified="2024-01-20",
            publisher_name="Tech Blog",
            publisher_logo="https://example.com/logo.png",
            image=["https://example.com/python-cover.jpg"],
            description="A comprehensive guide to mastering Python programming",
            wordCount=1500
        )

        # Validate all fields
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Article"
        assert schema["headline"] == "How to Master Python Programming"
        assert schema["url"] == "https://example.com/blog/python-guide"
        
        # CRITICAL: articleBody MUST exist
        assert "articleBody" in schema, "Article MUST have articleBody"
        article_body = schema["articleBody"]
        assert "most popular programming languages" in article_body
        assert "comprehensive guide" in article_body
        assert "basic syntax to advanced concepts" in article_body
        
        # Author
        assert schema["author"]["@type"] == "Person"
        assert schema["author"]["name"] == "John Doe"
        assert schema["author"]["url"] == "https://example.com/authors/john"
        
        # Dates
        assert "2024-01-15" in schema["datePublished"]
        assert "2024-01-20" in schema["dateModified"]
        
        # Publisher
        assert schema["publisher"]["@type"] == "Organization"
        assert schema["publisher"]["name"] == "Tech Blog"
        assert schema["publisher"]["logo"]["@type"] == "ImageObject"
        
        # Image
        assert len(schema["image"]) == 1
        assert schema["image"][0]["url"] == "https://example.com/python-cover.jpg"
        
        # Optional fields
        assert schema["description"] == "A comprehensive guide to mastering Python programming"
        assert schema["wordCount"] == 1500

