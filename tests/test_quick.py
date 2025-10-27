#!/usr/bin/env python3
"""
Quick Test Script for Schema Validator Pro
Run this to verify all core functionality works
"""

import sys
import json
from backend.services.schema_generator import SchemaGenerator
from backend.services.schema_validator import SchemaValidator


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def test_schema_generator():
    """Test schema generation for all types"""
    print_header("Testing Schema Generator")
    
    generator = SchemaGenerator()
    
    # Test 1: Check supported types
    types = generator.get_supported_types()
    if len(types) == 9:
        print_success(f"All 9 schema types supported: {', '.join(types)}")
    else:
        print_error(f"Expected 9 types, got {len(types)}")
        return False
    
    # Test 2: Generate Article schema
    print_info("Generating Article schema...")
    article = generator.generate(
        "Article",
        "Test Article Title\n\nThis is the article content.",
        url="https://example.com/article",
        author="John Doe",
        datePublished="2024-01-15"
    )
    
    if article["@type"] == "Article" and article["author"]["name"] == "John Doe":
        print_success("Article schema generated correctly")
    else:
        print_error("Article schema generation failed")
        return False
    
    # Test 3: Generate Product schema
    print_info("Generating Product schema...")
    product = generator.generate(
        "Product",
        "Amazing Product\n\nBest product ever.",
        name="Test Product",
        brand="Test Brand"
    )
    
    if product["@type"] == "Product" and product.get("brand", {}).get("name") == "Test Brand":
        print_success("Product schema generated correctly")
    else:
        print_error("Product schema generation failed")
        return False
    
    # Test 4: Validate schema
    print_info("Validating generated schema...")
    if generator.validate_schema(article):
        print_success("Schema validation passed")
    else:
        print_error("Schema validation failed")
        return False
    
    return True


def test_schema_validator():
    """Test schema validation functionality"""
    print_header("Testing Schema Validator")
    
    validator = SchemaValidator()
    
    # Test 1: Validate valid schema
    print_info("Testing valid schema...")
    valid_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Test Article",
        "author": {"@type": "Person", "name": "John Doe"}
    }
    
    is_valid, errors, warnings = validator.validate(valid_schema)
    
    if is_valid and len(errors) == 0:
        print_success("Valid schema passed validation")
    else:
        print_error(f"Valid schema failed: {errors}")
        return False
    
    # Test 2: Detect missing required fields
    print_info("Testing invalid schema (missing required fields)...")
    invalid_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Test"
        # Missing author
    }
    
    is_valid, errors, warnings = validator.validate(invalid_schema)
    
    if not is_valid and len(errors) > 0:
        print_success(f"Invalid schema detected: {errors[0]}")
    else:
        print_error("Failed to detect invalid schema")
        return False
    
    # Test 3: Calculate completeness score
    print_info("Testing completeness scoring...")
    score = validator.calculate_completeness_score(valid_schema)
    
    if 0 <= score <= 100:
        print_success(f"Completeness score calculated: {score}%")
    else:
        print_error(f"Invalid completeness score: {score}")
        return False
    
    # Test 4: Get optimization suggestions
    print_info("Testing optimization suggestions...")
    suggestions = validator.get_optimization_suggestions(valid_schema)
    
    if len(suggestions) > 0:
        print_success(f"Generated {len(suggestions)} optimization suggestions")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"   {i}. {suggestion}")
    else:
        print_error("No optimization suggestions generated")
        return False
    
    return True


def test_integration():
    """Test integration between generator and validator"""
    print_header("Testing Generator + Validator Integration")
    
    generator = SchemaGenerator()
    validator = SchemaValidator()
    
    # Generate schema for all 9 types
    test_cases = [
        ("Article", "Article Title\n\nContent here."),
        ("Product", "Product Name\n\nProduct description."),
        ("Recipe", "Recipe Name\n\nRecipe description."),
        ("HowTo", "How-To Title\n\n1. Step one\n2. Step two"),
        ("FAQPage", "What is this?\nThis is a test.\n\nHow does it work?\nIt works well."),
        ("Event", "Event Name\n\nEvent description."),
        ("Person", "John Doe\n\nSoftware Engineer"),
        ("Organization", "Company Name\n\nCompany description."),
        ("Course", "Course Name\n\nCourse description.")
    ]
    
    passed = 0
    failed = 0
    
    for schema_type, content in test_cases:
        print_info(f"Testing {schema_type}...")
        
        try:
            # Generate schema
            if schema_type == "Recipe":
                schema = generator.generate(
                    schema_type,
                    content,
                    recipeIngredient=["ingredient1"],
                    recipeInstructions=["instruction1"]
                )
            elif schema_type == "Event":
                schema = generator.generate(
                    schema_type,
                    content,
                    startDate="2024-06-15",
                    location={"@type": "Place", "name": "Venue"}
                )
            elif schema_type == "Course":
                schema = generator.generate(
                    schema_type,
                    content,
                    provider={"@type": "Organization", "name": "Provider"}
                )
            else:
                schema = generator.generate(schema_type, content)
            
            # Validate schema
            is_valid, errors, warnings = validator.validate(schema)
            
            # Calculate score
            score = validator.calculate_completeness_score(schema)
            
            if is_valid:
                print_success(f"{schema_type}: Valid (Score: {score}%)")
                passed += 1
            else:
                print_error(f"{schema_type}: Invalid - {errors}")
                failed += 1
                
        except Exception as e:
            print_error(f"{schema_type}: Exception - {str(e)}")
            failed += 1
    
    print_info(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


def main():
    """Run all tests"""
    print_header("Schema Validator Pro - Quick Test Suite")
    print_info("Testing core functionality...")
    
    all_passed = True
    
    # Test 1: Schema Generator
    if not test_schema_generator():
        all_passed = False
    
    # Test 2: Schema Validator
    if not test_schema_validator():
        all_passed = False
    
    # Test 3: Integration
    if not test_integration():
        all_passed = False
    
    # Final result
    print_header("Test Results")
    
    if all_passed:
        print_success("ALL TESTS PASSED! ✨")
        print_info("Schema Validator Pro is ready for deployment!")
        return 0
    else:
        print_error("SOME TESTS FAILED")
        print_info("Please fix the issues before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())

