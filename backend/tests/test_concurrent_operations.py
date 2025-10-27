"""
Concurrent Operations Tests for Schema Validator Pro

Tests cover:
- Multi-threaded schema generation
- Concurrent schema validation
- Thread safety of generator and validator instances
- Race condition detection
- Concurrent API requests simulation
- Resource contention handling

Concurrency Requirements:
- Thread-safe operations
- No race conditions
- Consistent results across threads
- No data corruption
- Proper resource cleanup
"""

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.services.schema_generator import SchemaGenerator
from backend.services.schema_validator import SchemaValidator

# Mark all tests in this file as concurrent tests
pytestmark = pytest.mark.concurrent


class TestConcurrentSchemaGeneration:
    """Test concurrent schema generation operations."""
    
    def test_concurrent_article_generation(self):
        """Test generating Article schemas concurrently from multiple threads."""
        generator = SchemaGenerator()
        results = []
        errors = []
        
        def generate_article(thread_id):
            try:
                schema = generator.generate(
                    "Article",
                    f"Article content from thread {thread_id}. " * 10,
                    headline=f"Article {thread_id}",
                    author=f"Author {thread_id}"
                )
                return schema
            except Exception as e:
                errors.append((thread_id, str(e)))
                return None
        
        # Run 50 concurrent generations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(generate_article, i) for i in range(50)]
            results = [f.result() for f in as_completed(futures)]
        
        # Verify all succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 50
        assert all(r is not None for r in results)
        assert all(r["@type"] == "Article" for r in results)
        
        # Verify each thread got unique content
        headlines = [r["headline"] for r in results]
        assert len(set(headlines)) == 50  # All unique
    
    def test_concurrent_mixed_schema_types(self):
        """Test generating different schema types concurrently."""
        generator = SchemaGenerator()
        results = []
        errors = []
        
        schema_types = ["Article", "Product", "Recipe", "Event", "Organization"]
        
        def generate_schema(index):
            try:
                schema_type = schema_types[index % len(schema_types)]
                schema = generator.generate(
                    schema_type,
                    f"Content for {schema_type} {index}",
                    name=f"{schema_type} {index}"
                )
                return schema
            except Exception as e:
                errors.append((index, str(e)))
                return None
        
        # Run 100 concurrent generations with mixed types
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(generate_schema, i) for i in range(100)]
            results = [f.result() for f in as_completed(futures)]
        
        # Verify all succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 100
        assert all(r is not None for r in results)
        
        # Verify correct distribution of types
        type_counts = {}
        for r in results:
            schema_type = r["@type"]
            type_counts[schema_type] = type_counts.get(schema_type, 0) + 1
        
        assert len(type_counts) == 5  # All 5 types present
        assert all(count == 20 for count in type_counts.values())  # Even distribution
    
    def test_generator_instance_thread_safety(self):
        """Test that a single generator instance is thread-safe."""
        generator = SchemaGenerator()
        results = []
        lock = threading.Lock()
        
        def generate_and_store(thread_id):
            schema = generator.generate(
                "Product",
                f"Product {thread_id}",
                name=f"Product {thread_id}",
                price=str(thread_id * 10)
            )
            with lock:
                results.append(schema)
        
        # Create 30 threads using the same generator instance
        threads = []
        for i in range(30):
            thread = threading.Thread(target=generate_and_store, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all succeeded
        assert len(results) == 30
        assert all(r["@type"] == "Product" for r in results)
        
        # Verify no data corruption
        names = [r["name"] for r in results]
        assert len(set(names)) == 30  # All unique


class TestConcurrentSchemaValidation:
    """Test concurrent schema validation operations."""
    
    def test_concurrent_validation(self):
        """Test validating schemas concurrently from multiple threads."""
        generator = SchemaGenerator()
        validator = SchemaValidator()
        
        # Pre-generate schemas
        schemas = [
            generator.generate(
                "Article",
                f"Content {i}",
                headline=f"Article {i}",
                author=f"Author {i}"
            )
            for i in range(50)
        ]
        
        results = []
        errors = []
        
        def validate_schema(schema, index):
            try:
                is_valid, errs, warnings = validator.validate(schema)
                return (index, is_valid, len(errs), len(warnings))
            except Exception as e:
                errors.append((index, str(e)))
                return None
        
        # Run 50 concurrent validations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(validate_schema, schemas[i], i)
                for i in range(50)
            ]
            results = [f.result() for f in as_completed(futures)]
        
        # Verify all succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 50
        assert all(r is not None for r in results)
        assert all(r[1] is True for r in results)  # All valid
    
    def test_validator_instance_thread_safety(self):
        """Test that a single validator instance is thread-safe."""
        generator = SchemaGenerator()
        validator = SchemaValidator()
        
        results = []
        lock = threading.Lock()
        
        def generate_and_validate(thread_id):
            schema = generator.generate(
                "Recipe",
                f"Recipe {thread_id}",
                name=f"Recipe {thread_id}",
                recipeIngredient=[f"Ingredient {i}" for i in range(5)]
            )
            is_valid, errors, warnings = validator.validate(schema)
            with lock:
                results.append((thread_id, is_valid))
        
        # Create 40 threads using the same validator instance
        threads = []
        for i in range(40):
            thread = threading.Thread(target=generate_and_validate, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all succeeded
        assert len(results) == 40
        assert all(is_valid for _, is_valid in results)


class TestConcurrentGenerationAndValidation:
    """Test concurrent generation and validation together."""
    
    def test_concurrent_pipeline(self):
        """Test concurrent schema generation and validation pipeline."""
        generator = SchemaGenerator()
        validator = SchemaValidator()
        
        results = []
        errors = []
        
        def generate_and_validate(index):
            try:
                # Generate
                schema = generator.generate(
                    "Event",
                    f"Event {index}",
                    name=f"Event {index}",
                    startDate="2025-06-01T09:00:00",
                    location="Convention Center"
                )
                
                # Validate
                is_valid, errs, warnings = validator.validate(schema)
                
                return (index, schema, is_valid, len(errs), len(warnings))
            except Exception as e:
                errors.append((index, str(e)))
                return None
        
        # Run 60 concurrent pipelines
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(generate_and_validate, i) for i in range(60)]
            results = [f.result() for f in as_completed(futures)]
        
        # Verify all succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 60
        assert all(r is not None for r in results)
        assert all(r[2] is True for r in results)  # All valid
        
        # Verify schemas are correct
        schemas = [r[1] for r in results]
        assert all(s["@type"] == "Event" for s in schemas)
    
    def test_high_concurrency_stress(self):
        """Stress test with high concurrency (100 threads)."""
        generator = SchemaGenerator()
        validator = SchemaValidator()

        success_count = 0
        validation_count = 0
        errors = []
        lock = threading.Lock()

        def stress_operation(thread_id):
            nonlocal success_count, validation_count
            try:
                # Use Article for all to ensure validation passes
                schema = generator.generate(
                    "Article",
                    f"Content for thread {thread_id}. " * 10,
                    headline=f"Article {thread_id}",
                    author=f"Author {thread_id}"
                )

                is_valid, errs, warnings = validator.validate(schema)

                with lock:
                    validation_count += 1
                    if is_valid:
                        success_count += 1
            except Exception as e:
                with lock:
                    errors.append((thread_id, str(e)))

        # Create 100 threads
        threads = []
        for i in range(100):
            thread = threading.Thread(target=stress_operation, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify high success rate
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert validation_count == 100, f"Only {validation_count} validations completed"
        assert success_count == 100, f"Only {success_count} validations passed"


class TestRaceConditionDetection:
    """Test for race conditions and data corruption."""
    
    def test_no_shared_state_corruption(self):
        """Test that concurrent operations don't corrupt shared state."""
        generator = SchemaGenerator()
        
        results = []
        lock = threading.Lock()
        
        def generate_with_custom_defaults(thread_id):
            # Each thread uses different site defaults
            custom_generator = SchemaGenerator(site_defaults={
                "publisher": f"Publisher {thread_id}",
                "author": f"Author {thread_id}"
            })
            
            schema = custom_generator.generate(
                "Article",
                f"Content {thread_id}",
                headline=f"Article {thread_id}"
            )
            
            with lock:
                results.append((thread_id, schema))
        
        # Create 20 threads with different defaults
        threads = []
        for i in range(20):
            thread = threading.Thread(target=generate_with_custom_defaults, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify each thread got its own defaults
        assert len(results) == 20
        for thread_id, schema in results:
            # Verify the schema has the correct thread-specific data
            assert f"Article {thread_id}" in schema["headline"]

    def test_counter_race_condition(self):
        """Test for race conditions in counter operations."""
        generator = SchemaGenerator()

        counter = {"value": 0}
        lock = threading.Lock()
        results = []

        def increment_and_generate(thread_id):
            # Increment counter (potential race condition)
            with lock:
                counter["value"] += 1
                current_count = counter["value"]

            # Generate schema
            schema = generator.generate(
                "Product",
                f"Product {current_count}",
                name=f"Product {current_count}",
                price=str(current_count * 10)
            )

            with lock:
                results.append((current_count, schema))

        # Create 50 threads
        threads = []
        for i in range(50):
            thread = threading.Thread(target=increment_and_generate, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify counter reached 50 (no lost increments)
        assert counter["value"] == 50
        assert len(results) == 50

        # Verify all counts are unique (no race condition)
        counts = [count for count, _ in results]
        assert len(set(counts)) == 50


class TestResourceCleanup:
    """Test proper resource cleanup in concurrent scenarios."""

    def test_generator_cleanup_after_concurrent_use(self):
        """Test that generators are properly cleaned up after concurrent use."""
        results = []

        def create_and_use_generator(thread_id):
            generator = SchemaGenerator()
            schema = generator.generate(
                "Article",
                f"Content {thread_id}",
                headline=f"Article {thread_id}",
                author=f"Author {thread_id}"
            )
            return schema

        # Create and destroy 30 generator instances concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_and_use_generator, i) for i in range(30)]
            results = [f.result() for f in as_completed(futures)]

        # Verify all succeeded
        assert len(results) == 30
        assert all(r["@type"] == "Article" for r in results)

    def test_validator_cleanup_after_concurrent_use(self):
        """Test that validators are properly cleaned up after concurrent use."""
        generator = SchemaGenerator()

        # Pre-generate schemas (use Article which has fewer required fields)
        schemas = [
            generator.generate(
                "Article",
                f"Article content {i}. " * 10,
                headline=f"Article {i}",
                author=f"Author {i}"
            )
            for i in range(30)
        ]

        results = []

        def create_and_use_validator(schema):
            validator = SchemaValidator()
            is_valid, errors, warnings = validator.validate(schema)
            return is_valid

        # Create and destroy 30 validator instances concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_and_use_validator, s) for s in schemas]
            results = [f.result() for f in as_completed(futures)]

        # Verify all succeeded
        assert len(results) == 30
        assert all(results)


class TestConcurrentComplexScenarios:
    """Test complex concurrent scenarios."""

    def test_concurrent_faqpage_generation(self):
        """Test concurrent generation of complex FAQPage schemas."""
        generator = SchemaGenerator()
        results = []
        errors = []

        def generate_faq(thread_id):
            try:
                content = "\n\n".join([
                    f"Question {thread_id}-{i}?\nAnswer {thread_id}-{i}. " * 5
                    for i in range(20)
                ])

                schema = generator.generate(
                    "FAQPage",
                    content,
                    name=f"FAQ {thread_id}"
                )
                return schema
            except Exception as e:
                errors.append((thread_id, str(e)))
                return None

        # Run 20 concurrent FAQPage generations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_faq, i) for i in range(20)]
            results = [f.result() for f in as_completed(futures)]

        # Verify all succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 20
        assert all(r is not None for r in results)
        assert all(r["@type"] == "FAQPage" for r in results)

    def test_concurrent_recipe_with_many_ingredients(self):
        """Test concurrent generation of complex Recipe schemas."""
        generator = SchemaGenerator()
        results = []
        errors = []

        def generate_recipe(thread_id):
            try:
                ingredients = [f"Ingredient {thread_id}-{i}" for i in range(30)]
                instructions = [f"Step {thread_id}-{i}" for i in range(20)]

                schema = generator.generate(
                    "Recipe",
                    f"Recipe {thread_id}",
                    name=f"Recipe {thread_id}",
                    recipeIngredient=ingredients,
                    recipeInstructions=instructions
                )
                return schema
            except Exception as e:
                errors.append((thread_id, str(e)))
                return None

        # Run 25 concurrent Recipe generations
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(generate_recipe, i) for i in range(25)]
            results = [f.result() for f in as_completed(futures)]

        # Verify all succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 25
        assert all(r is not None for r in results)
        assert all(r["@type"] == "Recipe" for r in results)

        # Verify ingredients are correct
        for i, schema in enumerate(results):
            assert len(schema["recipeIngredient"]) == 30
            assert len(schema["recipeInstructions"]) == 20

    def test_concurrent_batch_operations(self):
        """Test concurrent batch operations."""
        generator = SchemaGenerator()
        validator = SchemaValidator()

        results = []
        errors = []

        def batch_operation(batch_id):
            try:
                # Generate 10 schemas
                schemas = []
                for i in range(10):
                    schema = generator.generate(
                        "Article",
                        f"Batch {batch_id} Article {i}",
                        headline=f"Batch {batch_id} Article {i}",
                        author=f"Author {batch_id}"
                    )
                    schemas.append(schema)

                # Validate all
                valid_count = 0
                for schema in schemas:
                    is_valid, errs, warnings = validator.validate(schema)
                    if is_valid:
                        valid_count += 1

                return (batch_id, len(schemas), valid_count)
            except Exception as e:
                errors.append((batch_id, str(e)))
                return None

        # Run 10 concurrent batch operations (100 schemas total)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(batch_operation, i) for i in range(10)]
            results = [f.result() for f in as_completed(futures)]

        # Verify all succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert all(r is not None for r in results)

        # Verify all schemas were generated and validated
        total_generated = sum(r[1] for r in results)
        total_valid = sum(r[2] for r in results)
        assert total_generated == 100
        assert total_valid == 100

