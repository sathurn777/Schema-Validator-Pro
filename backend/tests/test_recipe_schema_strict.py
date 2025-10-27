"""
Strict Recipe Schema Generation Tests

This file contains STRICT tests for Recipe schema generation.
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


class TestRecipeSchemaIngredientsGeneration:
    """
    CRITICAL: Test Recipe recipeIngredient generation.
    
    This is a required field for Recipe schema.
    """

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_recipe_with_ingredients_list(self):
        """Test Recipe with ingredients as list."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Chocolate Chip Cookies",
            recipeIngredient=[
                "2 cups all-purpose flour",
                "1 cup butter",
                "1 cup sugar",
                "2 eggs",
                "1 tsp vanilla extract",
                "2 cups chocolate chips"
            ]
        )

        assert "recipeIngredient" in schema, "Recipe MUST have recipeIngredient"
        ingredients = schema["recipeIngredient"]
        assert isinstance(ingredients, list), "recipeIngredient must be a list"
        assert len(ingredients) == 6, "Should have 6 ingredients"
        assert "2 cups all-purpose flour" in ingredients
        assert "2 cups chocolate chips" in ingredients

    def test_recipe_without_ingredients_has_default(self):
        """Test Recipe without ingredients gets default."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Simple Recipe"
        )

        assert "recipeIngredient" in schema
        assert isinstance(schema["recipeIngredient"], list)
        assert len(schema["recipeIngredient"]) > 0

    def test_recipe_with_single_ingredient(self):
        """Test Recipe with single ingredient."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Simple Recipe",
            recipeIngredient=["1 cup water"]
        )

        assert len(schema["recipeIngredient"]) == 1
        assert schema["recipeIngredient"][0] == "1 cup water"


class TestRecipeSchemaInstructionsGeneration:
    """
    CRITICAL: Test Recipe recipeInstructions generation.
    
    This is a required field and should be structured as HowToStep array.
    """

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_recipe_with_instructions_string(self):
        """Test Recipe with instructions as multi-line string."""
        instructions = """Preheat oven to 350°F
Mix flour and butter
Add eggs and vanilla
Fold in chocolate chips
Bake for 12 minutes"""

        schema = self.generator.generate(
            schema_type="Recipe",
            content="Chocolate Chip Cookies",
            recipeInstructions=instructions
        )

        assert "recipeInstructions" in schema, "Recipe MUST have recipeInstructions"
        steps = schema["recipeInstructions"]
        assert isinstance(steps, list), "recipeInstructions must be a list"
        assert len(steps) == 5, "Should have 5 steps"
        
        # Verify HowToStep structure
        for i, step in enumerate(steps):
            assert step["@type"] == "HowToStep", f"Step {i} must be HowToStep type"
            assert "text" in step, f"Step {i} must have text"
            assert "name" in step, f"Step {i} must have name"
            assert "position" in step, f"Step {i} must have position"
            assert step["position"] == i + 1, f"Step {i} position must be {i+1}"
        
        # Verify content
        assert "Preheat oven to 350°F" in steps[0]["text"]
        assert "Bake for 12 minutes" in steps[4]["text"]

    def test_recipe_with_instructions_list_of_strings(self):
        """Test Recipe with instructions as list of strings."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Simple Recipe",
            recipeInstructions=[
                "Mix ingredients",
                "Cook for 10 minutes",
                "Serve hot"
            ]
        )

        steps = schema["recipeInstructions"]
        assert len(steps) == 3
        
        for i, step in enumerate(steps):
            assert step["@type"] == "HowToStep"
            assert step["position"] == i + 1
        
        assert steps[0]["text"] == "Mix ingredients"
        assert steps[1]["text"] == "Cook for 10 minutes"
        assert steps[2]["text"] == "Serve hot"

    def test_recipe_with_instructions_list_of_dicts(self):
        """Test Recipe with instructions as list of HowToStep dicts."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Advanced Recipe",
            recipeInstructions=[
                {"text": "Prepare ingredients", "name": "Preparation"},
                {"text": "Cook on medium heat", "name": "Cooking"},
                {"text": "Let it cool", "name": "Cooling"}
            ]
        )

        steps = schema["recipeInstructions"]
        assert len(steps) == 3
        
        assert steps[0]["text"] == "Prepare ingredients"
        assert steps[0]["name"] == "Preparation"
        assert steps[1]["text"] == "Cook on medium heat"
        assert steps[1]["name"] == "Cooking"

    def test_recipe_without_instructions_has_default(self):
        """Test Recipe without instructions gets default."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Simple Recipe"
        )

        assert "recipeInstructions" in schema
        assert isinstance(schema["recipeInstructions"], list)
        assert len(schema["recipeInstructions"]) > 0
        assert schema["recipeInstructions"][0]["@type"] == "HowToStep"


class TestRecipeSchemaAuthorGeneration:
    """Test Recipe author field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_recipe_with_author_string(self):
        """Test Recipe with author as string."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Grandma's Cookies",
            author="Grandma Smith"
        )

        assert "author" in schema
        assert schema["author"]["@type"] == "Person"
        assert schema["author"]["name"] == "Grandma Smith"

    def test_recipe_with_author_dict(self):
        """Test Recipe with author as dict."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Chef's Special",
            author={
                "name": "Chef John",
                "url": "https://example.com/chef-john"
            }
        )

        assert "author" in schema
        author = schema["author"]
        assert author["@type"] == "Person"
        assert author["name"] == "Chef John"
        assert author["url"] == "https://example.com/chef-john"

    def test_recipe_without_author(self):
        """Test Recipe without author."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Simple Recipe"
        )

        # Author is optional for Recipe
        assert "author" not in schema or schema["author"] is not None


class TestRecipeNutritionGeneration:
    """Test Recipe nutrition field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_recipe_with_nutrition_dict(self):
        """Test Recipe with nutrition information."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Healthy Salad",
            nutrition={
                "calories": "150 calories",
                "fatContent": "5 grams",
                "proteinContent": "10 grams",
                "carbohydrateContent": "20 grams"
            }
        )

        assert "nutrition" in schema, "Recipe should have nutrition when provided"
        nutrition = schema["nutrition"]
        assert nutrition["@type"] == "NutritionInformation"
        assert nutrition["calories"] == "150 calories"
        assert nutrition["fatContent"] == "5 grams"
        assert nutrition["proteinContent"] == "10 grams"
        assert nutrition["carbohydrateContent"] == "20 grams"

    def test_recipe_without_nutrition(self):
        """Test Recipe without nutrition."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Simple Recipe"
        )

        # Nutrition is optional
        assert "nutrition" not in schema


class TestRecipeSchemaTimeFields:
    """Test Recipe time-related fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_recipe_with_all_time_fields(self):
        """Test Recipe with prepTime, cookTime, and totalTime."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Complex Recipe",
            prepTime="PT15M",  # ISO 8601 duration
            cookTime="PT30M",
            totalTime="PT45M"
        )

        assert schema["prepTime"] == "PT15M"
        assert schema["cookTime"] == "PT30M"
        assert schema["totalTime"] == "PT45M"

    def test_recipe_with_partial_time_fields(self):
        """Test Recipe with only some time fields."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Quick Recipe",
            prepTime="PT5M",
            cookTime="PT10M"
        )

        assert schema["prepTime"] == "PT5M"
        assert schema["cookTime"] == "PT10M"
        assert "totalTime" not in schema

    def test_recipe_without_time_fields(self):
        """Test Recipe without time fields."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Simple Recipe"
        )

        assert "prepTime" not in schema
        assert "cookTime" not in schema
        assert "totalTime" not in schema


class TestRecipeSchemaOptionalFields:
    """Test Recipe optional fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_recipe_with_yield(self):
        """Test Recipe with recipeYield."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Batch Recipe",
            recipeYield="24 cookies"
        )

        assert schema["recipeYield"] == "24 cookies"

    def test_recipe_with_category_and_cuisine(self):
        """Test Recipe with category and cuisine."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Italian Pasta",
            recipeCategory="Main Course",
            recipeCuisine="Italian"
        )

        assert schema["recipeCategory"] == "Main Course"
        assert schema["recipeCuisine"] == "Italian"

    def test_recipe_with_cooking_method(self):
        """Test Recipe with cookingMethod."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Grilled Chicken",
            cookingMethod="Grilling"
        )

        assert schema["cookingMethod"] == "Grilling"

    def test_recipe_with_keywords(self):
        """Test Recipe with keywords."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Healthy Recipe",
            keywords="healthy, low-carb, gluten-free"
        )

        assert schema["keywords"] == "healthy, low-carb, gluten-free"

    def test_recipe_with_aggregate_rating(self):
        """Test Recipe with aggregateRating."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Popular Recipe",
            aggregateRating={
                "ratingValue": "4.8",
                "reviewCount": "256"
            }
        )

        assert "aggregateRating" in schema
        rating = schema["aggregateRating"]
        assert rating["@type"] == "AggregateRating"
        assert rating["ratingValue"] == "4.8"
        assert rating["reviewCount"] == "256"


class TestRecipeSchemaImageGeneration:
    """Test Recipe image field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_recipe_with_single_image(self):
        """Test Recipe with single image."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Beautiful Dish",
            url="https://example.com/recipe",
            image="dish-photo.jpg"
        )

        assert "image" in schema
        assert isinstance(schema["image"], list)
        assert len(schema["image"]) == 1
        
        image = schema["image"][0]
        assert image["@type"] == "ImageObject"
        assert "dish-photo.jpg" in image["url"]

    def test_recipe_with_multiple_images(self):
        """Test Recipe with multiple images."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Step-by-Step Recipe",
            url="https://example.com/recipe",
            image=["step1.jpg", "step2.jpg", "final.jpg"]
        )

        assert "image" in schema
        assert len(schema["image"]) == 3
        
        for img in schema["image"]:
            assert img["@type"] == "ImageObject"

    def test_recipe_without_image(self):
        """Test Recipe without image."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Simple Recipe"
        )

        assert "image" not in schema


class TestRecipeSchemaComplete:
    """Test complete Recipe schema with all fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_recipe_complete_chocolate_chip_cookies(self):
        """Test complete Recipe schema for chocolate chip cookies."""
        schema = self.generator.generate(
            schema_type="Recipe",
            content="Grandma's Chocolate Chip Cookies",
            url="https://example.com/recipes/chocolate-chip-cookies",
            name="The Best Chocolate Chip Cookies",
            description="Soft, chewy chocolate chip cookies with a crispy edge",
            author={
                "name": "Grandma Smith",
                "url": "https://example.com/authors/grandma"
            },
            datePublished="2024-01-15",
            image=["cookies-final.jpg", "cookies-baking.jpg"],
            recipeIngredient=[
                "2 cups all-purpose flour",
                "1 cup butter, softened",
                "3/4 cup granulated sugar",
                "3/4 cup brown sugar",
                "2 large eggs",
                "2 tsp vanilla extract",
                "1 tsp baking soda",
                "1 tsp salt",
                "2 cups chocolate chips"
            ],
            recipeInstructions="""Preheat oven to 375°F (190°C)
Cream together butter and sugars until fluffy
Beat in eggs and vanilla
Mix in flour, baking soda, and salt
Fold in chocolate chips
Drop spoonfuls onto baking sheet
Bake for 9-11 minutes until golden
Cool on wire rack""",
            prepTime="PT15M",
            cookTime="PT11M",
            totalTime="PT26M",
            recipeYield="48 cookies",
            recipeCategory="Dessert",
            recipeCuisine="American",
            keywords="cookies, chocolate chip, dessert, baking",
            nutrition={
                "calories": "180 calories",
                "fatContent": "9 grams",
                "carbohydrateContent": "24 grams",
                "proteinContent": "2 grams",
                "sugarContent": "16 grams"
            },
            aggregateRating={
                "ratingValue": "4.9",
                "reviewCount": "1247"
            }
        )

        # Validate all fields
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Recipe"
        assert schema["name"] == "The Best Chocolate Chip Cookies"
        assert schema["url"] == "https://example.com/recipes/chocolate-chip-cookies"
        assert schema["description"] == "Soft, chewy chocolate chip cookies with a crispy edge"
        
        # Author
        assert schema["author"]["@type"] == "Person"
        assert schema["author"]["name"] == "Grandma Smith"
        
        # Ingredients - CRITICAL
        assert len(schema["recipeIngredient"]) == 9
        assert "2 cups all-purpose flour" in schema["recipeIngredient"]
        assert "2 cups chocolate chips" in schema["recipeIngredient"]
        
        # Instructions - CRITICAL
        assert len(schema["recipeInstructions"]) == 8
        assert schema["recipeInstructions"][0]["@type"] == "HowToStep"
        assert "Preheat oven" in schema["recipeInstructions"][0]["text"]
        assert "Cool on wire rack" in schema["recipeInstructions"][7]["text"]
        
        # Times
        assert schema["prepTime"] == "PT15M"
        assert schema["cookTime"] == "PT11M"
        assert schema["totalTime"] == "PT26M"
        
        # Yield and category
        assert schema["recipeYield"] == "48 cookies"
        assert schema["recipeCategory"] == "Dessert"
        assert schema["recipeCuisine"] == "American"
        
        # Nutrition
        assert schema["nutrition"]["@type"] == "NutritionInformation"
        assert schema["nutrition"]["calories"] == "180 calories"
        
        # Rating
        assert schema["aggregateRating"]["@type"] == "AggregateRating"
        assert schema["aggregateRating"]["ratingValue"] == "4.9"
        
        # Images
        assert len(schema["image"]) == 2

