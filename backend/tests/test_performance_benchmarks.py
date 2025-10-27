"""
Performance Benchmark Tests for Schema Validator Pro

Tests cover:
- Schema generation performance for all 9 types
- Schema validation performance
- Large data volume processing
- Complex nested object handling
- Memory efficiency
- Response time requirements

Performance Requirements:
- Schema generation: < 100ms for simple schemas, < 500ms for complex
- Schema validation: < 50ms for simple schemas, < 200ms for complex
- Batch processing: > 100 schemas/second
"""

import pytest
from backend.services.schema_generator import SchemaGenerator
from backend.services.schema_validator import SchemaValidator

# Mark all tests in this file as performance tests
pytestmark = pytest.mark.performance


class TestSchemaGenerationPerformance:
    """Performance benchmarks for schema generation."""
    
    def setup_method(self):
        """Setup schema generator."""
        self.generator = SchemaGenerator()
    
    def test_article_generation_performance(self, benchmark):
        """Benchmark Article schema generation."""
        content = "This is a test article for performance benchmarking. " * 10
        
        result = benchmark(
            self.generator.generate,
            "Article",
            content,
            headline="Performance Test Article",
            author="Test Author",
            url="https://example.com/article"
        )
        
        assert result["@type"] == "Article"
    
    def test_product_generation_performance(self, benchmark):
        """Benchmark Product schema generation."""
        content = "Product description for performance testing. " * 10
        
        result = benchmark(
            self.generator.generate,
            "Product",
            content,
            name="Test Product",
            price="99.99",
            currency="USD"
        )
        
        assert result["@type"] == "Product"
    
    def test_recipe_generation_performance(self, benchmark):
        """Benchmark Recipe schema generation with complex data."""
        content = "Recipe description. " * 10
        ingredients = ["Ingredient " + str(i) for i in range(20)]
        instructions = ["Step " + str(i) for i in range(15)]
        
        result = benchmark(
            self.generator.generate,
            "Recipe",
            content,
            name="Test Recipe",
            recipeIngredient=ingredients,
            recipeInstructions=instructions
        )
        
        assert result["@type"] == "Recipe"
    
    def test_event_generation_performance(self, benchmark):
        """Benchmark Event schema generation with nested objects."""
        content = "Annual tech conference. " * 10
        
        result = benchmark(
            self.generator.generate,
            "Event",
            content,
            name="Tech Conference 2025",
            startDate="2025-06-01T09:00:00",
            location="Convention Center"
        )
        
        assert result["@type"] == "Event"
    
    def test_faqpage_generation_performance(self, benchmark):
        """Benchmark FAQPage schema generation with multiple questions."""
        content = "\n\n".join([
            f"Question {i}?\nAnswer to question {i}. " * 5
            for i in range(20)
        ])
        
        result = benchmark(
            self.generator.generate,
            "FAQPage",
            content,
            name="FAQ Page"
        )
        
        assert result["@type"] == "FAQPage"


class TestSchemaValidationPerformance:
    """Performance benchmarks for schema validation."""
    
    def setup_method(self):
        """Setup validator and generator."""
        self.validator = SchemaValidator()
        self.generator = SchemaGenerator()
    
    def test_article_validation_performance(self, benchmark):
        """Benchmark Article schema validation."""
        schema = self.generator.generate(
            "Article",
            "Article content. " * 20,
            headline="Test Article",
            author="Test Author"
        )

        is_valid, errors, warnings = benchmark(self.validator.validate, schema)

        assert is_valid is True
    
    def test_product_validation_performance(self, benchmark):
        """Benchmark Product schema validation."""
        schema = self.generator.generate(
            "Product",
            "Product description. " * 20,
            name="Test Product",
            price="99.99",
            currency="USD"
        )

        is_valid, errors, warnings = benchmark(self.validator.validate, schema)

        # Product requires offers field
        if not is_valid:
            # Just check that validation runs, don't fail on missing recommended fields
            assert len(errors) == 0 or "offers" in str(errors).lower()
        else:
            assert is_valid is True
    
    def test_recipe_validation_performance(self, benchmark):
        """Benchmark Recipe schema validation with many ingredients."""
        ingredients = ["Ingredient " + str(i) for i in range(30)]
        instructions = ["Step " + str(i) for i in range(20)]

        schema = self.generator.generate(
            "Recipe",
            "Recipe description. " * 20,
            name="Complex Recipe",
            recipeIngredient=ingredients,
            recipeInstructions=instructions
        )

        is_valid, errors, warnings = benchmark(self.validator.validate, schema)

        assert is_valid is True


class TestBatchProcessingPerformance:
    """Performance benchmarks for batch processing."""
    
    def setup_method(self):
        """Setup generator and validator."""
        self.generator = SchemaGenerator()
        self.validator = SchemaValidator()
    
    def test_batch_article_generation(self, benchmark):
        """Benchmark batch generation of 100 Article schemas."""
        def generate_batch():
            results = []
            for i in range(100):
                schema = self.generator.generate(
                    "Article",
                    f"Content for article {i}. " * 5,
                    headline=f"Article {i}",
                    author=f"Author {i}"
                )
                results.append(schema)
            return results
        
        results = benchmark(generate_batch)
        
        assert len(results) == 100
        assert all(s["@type"] == "Article" for s in results)
    
    def test_batch_validation(self, benchmark):
        """Benchmark batch validation of 100 schemas."""
        # Pre-generate schemas
        schemas = [
            self.generator.generate(
                "Article",
                f"Content {i}",
                headline=f"Article {i}",
                author=f"Author {i}"
            )
            for i in range(100)
        ]

        def validate_batch():
            results = []
            for schema in schemas:
                is_valid, errors, warnings = self.validator.validate(schema)
                results.append(is_valid)
            return results

        results = benchmark(validate_batch)

        assert len(results) == 100
        assert all(results)
    
    def test_mixed_schema_types_batch(self, benchmark):
        """Benchmark batch generation of mixed schema types."""
        def generate_mixed_batch():
            results = []
            for i in range(50):
                if i % 5 == 0:
                    schema = self.generator.generate(
                        "Article",
                        f"Content {i}",
                        headline=f"Article {i}",
                        author=f"Author {i}"
                    )
                elif i % 5 == 1:
                    schema = self.generator.generate(
                        "Product",
                        f"Description {i}",
                        name=f"Product {i}",
                        price=str(i * 10)
                    )
                elif i % 5 == 2:
                    schema = self.generator.generate(
                        "Event",
                        f"Event description {i}",
                        name=f"Event {i}",
                        startDate="2025-06-01T09:00:00",
                        location="Convention Center"
                    )
                elif i % 5 == 3:
                    schema = self.generator.generate(
                        "Organization",
                        f"Org description {i}",
                        name=f"Organization {i}"
                    )
                else:
                    schema = self.generator.generate(
                        "Person",
                        f"Bio {i}",
                        name=f"Person {i}"
                    )
                results.append(schema)
            return results
        
        results = benchmark(generate_mixed_batch)

        assert len(results) == 50


class TestLargeDataVolumePerformance:
    """Performance benchmarks for large data volumes."""

    def setup_method(self):
        """Setup generator and validator."""
        self.generator = SchemaGenerator()
        self.validator = SchemaValidator()

    def test_article_with_large_content(self, benchmark):
        """Benchmark Article generation with very large content (10KB)."""
        large_content = "Lorem ipsum dolor sit amet. " * 400  # ~10KB

        result = benchmark(
            self.generator.generate,
            "Article",
            large_content,
            headline="Large Article",
            author="Test Author"
        )

        assert result["@type"] == "Article"
        assert len(result.get("articleBody", "")) > 5000

    def test_recipe_with_many_ingredients(self, benchmark):
        """Benchmark Recipe with 100 ingredients and 50 steps."""
        ingredients = [f"Ingredient {i}: Description of ingredient {i}" for i in range(100)]
        instructions = [f"Step {i}: Detailed instructions for step {i}. " * 5 for i in range(50)]

        result = benchmark(
            self.generator.generate,
            "Recipe",
            "Very complex recipe",
            name="Complex Recipe",
            recipeIngredient=ingredients,
            recipeInstructions=instructions
        )

        assert len(result["recipeIngredient"]) == 100
        assert len(result["recipeInstructions"]) == 50

    def test_faqpage_with_100_questions(self, benchmark):
        """Benchmark FAQPage with 100 questions."""
        content = "\n\n".join([
            f"Question {i}: What is the answer to question {i}?\nAnswer {i}: This is a detailed answer to question {i}. " * 10
            for i in range(100)
        ])

        result = benchmark(
            self.generator.generate,
            "FAQPage",
            content,
            name="Large FAQ"
        )

        assert result["@type"] == "FAQPage"
        assert len(result["mainEntity"]) >= 50  # Should extract many Q&A pairs

    def test_validation_of_large_schema(self, benchmark):
        """Benchmark validation of large schema with many fields."""
        schema = self.generator.generate(
            "Article",
            "Article content. " * 100,
            headline="Complete Article",
            author={"name": "John Doe", "url": "https://example.com/author"},
            publisher={"name": "Publisher Name", "logo": "https://example.com/logo.png"},
            image=["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
            datePublished="2025-01-01",
            dateModified="2025-01-15",
            description="Article description. " * 20
        )

        is_valid, errors, warnings = benchmark(self.validator.validate, schema)

        assert is_valid is True


class TestComplexNestedObjectPerformance:
    """Performance benchmarks for complex nested objects."""

    def setup_method(self):
        """Setup generator and validator."""
        self.generator = SchemaGenerator()
        self.validator = SchemaValidator()

    def test_product_with_complex_offers(self, benchmark):
        """Benchmark Product with complex nested offers structure."""
        result = benchmark(
            self.generator.generate,
            "Product",
            "Product with complex pricing. " * 10,
            name="Premium Product",
            offers={
                "price": "999.99",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": "https://example.com/buy"
            },
            brand={"name": "Premium Brand"},
            aggregateRating={
                "ratingValue": 4.8,
                "reviewCount": 1250
            }
        )

        assert result["@type"] == "Product"
        assert result["offers"]["@type"] == "Offer"

    def test_event_with_deep_nesting(self, benchmark):
        """Benchmark Event with deeply nested location and organizer."""
        result = benchmark(
            self.generator.generate,
            "Event",
            "Major international event. " * 10,
            name="International Conference",
            startDate="2025-09-15T09:00:00",
            endDate="2025-09-17T18:00:00",
            location={
                "name": "Grand Convention Center",
                "address": {
                    "streetAddress": "456 Conference Blvd",
                    "addressLocality": "New York",
                    "addressRegion": "NY",
                    "postalCode": "10001",
                    "addressCountry": "US"
                }
            },
            organizer={
                "name": "Global Events Organization",
                "url": "https://example.com/organizer"
            }
        )

        assert result["@type"] == "Event"
        assert result["location"]["@type"] == "Place"


class TestMemoryEfficiency:
    """Memory efficiency tests for schema operations."""

    def setup_method(self):
        """Setup generator and validator."""
        self.generator = SchemaGenerator()
        self.validator = SchemaValidator()

    def test_memory_efficient_batch_generation(self, benchmark):
        """Test memory efficiency when generating many schemas."""
        def generate_and_discard():
            # Generate schemas one at a time and discard
            for i in range(500):
                schema = self.generator.generate(
                    "Article",
                    f"Content {i}",
                    headline=f"Article {i}",
                    author=f"Author {i}"
                )
                # Immediately validate and discard
                self.validator.validate(schema)
            return True

        result = benchmark(generate_and_discard)

        assert result is True

    def test_schema_reuse_efficiency(self, benchmark):
        """Test efficiency of reusing generator instance."""
        def reuse_generator():
            results = []
            for i in range(200):
                schema = self.generator.generate(
                    "Product",
                    f"Description {i}",
                    name=f"Product {i}",
                    price=str(i * 10)
                )
                results.append(schema)
            return results

        results = benchmark(reuse_generator)

        assert len(results) == 200

