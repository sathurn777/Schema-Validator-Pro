"""
Strict Tests for FAQPage, HowTo, and Course Schema Generation

This file contains STRICT tests for the remaining schema types:
- FAQPage schema (8 tests)
- HowTo schema (8 tests)
- Course schema (8 tests)

Test Philosophy:
- Test REAL business logic, not just syntax
- Verify ACTUAL field values, not just field existence
- Test ALL parameter combinations
- NO mocking of core business logic
- NO skipping failures - fix code or adjust expectations
"""

import pytest
from backend.services.schema_generator import SchemaGenerator


class TestFAQPageSchemaStrict:
    """Strict tests for FAQPage schema generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SchemaGenerator()

    def test_faqpage_minimal_required_fields(self):
        """Test FAQPage with only required fields."""
        schema = self.generator.generate(
            schema_type="FAQPage",
            content="Frequently Asked Questions",
            name="Frequently Asked Questions",
            questions=[
                {
                    "question": "What is Schema.org?",
                    "answer": "Schema.org is a collaborative project to create structured data markup."
                }
            ]
        )

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "FAQPage"
        assert "mainEntity" in schema
        assert len(schema["mainEntity"]) == 1
        assert schema["mainEntity"][0]["@type"] == "Question"
        assert schema["mainEntity"][0]["name"] == "What is Schema.org?"
        assert schema["mainEntity"][0]["acceptedAnswer"]["@type"] == "Answer"
        assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == "Schema.org is a collaborative project to create structured data markup."

    def test_faqpage_multiple_questions(self):
        """Test FAQPage with multiple questions."""
        schema = self.generator.generate(
            schema_type="FAQPage",
            content="Product FAQ",
            name="Product FAQ",
            questions=[
                {"question": "Q1", "answer": "A1"},
                {"question": "Q2", "answer": "A2"},
                {"question": "Q3", "answer": "A3"}
            ]
        )

        assert len(schema["mainEntity"]) == 3
        assert schema["mainEntity"][0]["name"] == "Q1"
        assert schema["mainEntity"][1]["name"] == "Q2"
        assert schema["mainEntity"][2]["name"] == "Q3"
        assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == "A1"
        assert schema["mainEntity"][1]["acceptedAnswer"]["text"] == "A2"
        assert schema["mainEntity"][2]["acceptedAnswer"]["text"] == "A3"

    def test_faqpage_with_url(self):
        """Test FAQPage with URL."""
        schema = self.generator.generate(
            schema_type="FAQPage",
            content="FAQ",
            name="FAQ",
            url="https://example.com/faq",
            questions=[{"question": "Q", "answer": "A"}]
        )

        assert schema["url"] == "https://example.com/faq"

    def test_faqpage_with_description(self):
        """Test FAQPage with description."""
        schema = self.generator.generate(
            schema_type="FAQPage",
            content="FAQ",
            name="FAQ",
            description="Common questions about our product",
            questions=[{"question": "Q", "answer": "A"}]
        )

        assert schema["description"] == "Common questions about our product"

    def test_faqpage_with_long_answers(self):
        """Test FAQPage with long, detailed answers."""
        long_answer = "This is a very detailed answer that spans multiple sentences. " * 10

        schema = self.generator.generate(
            schema_type="FAQPage",
            content="FAQ",
            name="FAQ",
            questions=[
                {"question": "Complex question?", "answer": long_answer}
            ]
        )

        assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == long_answer
        assert len(schema["mainEntity"][0]["acceptedAnswer"]["text"]) > 100

    def test_faqpage_with_special_characters(self):
        """Test FAQPage with special characters in questions/answers."""
        schema = self.generator.generate(
            schema_type="FAQPage",
            content="FAQ",
            name="FAQ",
            questions=[
                {
                    "question": "What's the price? (USD)",
                    "answer": "It's $99.99 - that's 50% off!"
                }
            ]
        )

        assert schema["mainEntity"][0]["name"] == "What's the price? (USD)"
        assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == "It's $99.99 - that's 50% off!"

    def test_faqpage_with_unicode(self):
        """Test FAQPage with Unicode characters."""
        schema = self.generator.generate(
            schema_type="FAQPage",
            content="常见问题",
            name="常见问题",
            questions=[
                {"question": "什么是 Schema.org？", "answer": "Schema.org 是一个结构化数据标记项目。"}
            ]
        )

        assert schema["name"] == "常见问题"
        assert schema["mainEntity"][0]["name"] == "什么是 Schema.org？"
        assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == "Schema.org 是一个结构化数据标记项目。"

    def test_faqpage_empty_questions_list(self):
        """Test FAQPage with empty questions list."""
        schema = self.generator.generate(
            schema_type="FAQPage",
            content="FAQ",
            name="FAQ",
            questions=[]
        )

        # Should still generate valid schema, just with empty mainEntity
        assert schema["@type"] == "FAQPage"
        assert "mainEntity" in schema
        assert schema["mainEntity"] == []


class TestHowToSchemaStrict:
    """Strict tests for HowTo schema generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SchemaGenerator()

    def test_howto_minimal_required_fields(self):
        """Test HowTo with only required fields."""
        schema = self.generator.generate(
            schema_type="HowTo",
            content="How to Make Coffee",
            name="How to Make Coffee",
            steps=[
                {"text": "Boil water"},
                {"text": "Add coffee grounds"},
                {"text": "Pour water over grounds"}
            ]
        )

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "HowTo"
        assert schema["name"] == "How to Make Coffee"
        assert "step" in schema
        assert len(schema["step"]) == 3
        assert schema["step"][0]["@type"] == "HowToStep"
        assert schema["step"][0]["text"] == "Boil water"
        assert schema["step"][1]["text"] == "Add coffee grounds"
        assert schema["step"][2]["text"] == "Pour water over grounds"

    def test_howto_with_description(self):
        """Test HowTo with description."""
        schema = self.generator.generate(
            schema_type="HowTo",
            content="How to Bake Bread",
            name="How to Bake Bread",
            description="A simple guide to baking homemade bread",
            steps=[{"text": "Mix ingredients"}]
        )

        assert schema["description"] == "A simple guide to baking homemade bread"

    def test_howto_with_total_time(self):
        """Test HowTo with totalTime."""
        schema = self.generator.generate(
            schema_type="HowTo",
            content="How to Cook Pasta",
            name="How to Cook Pasta",
            totalTime="PT15M",
            steps=[{"text": "Boil water"}]
        )

        assert schema["totalTime"] == "PT15M"

    def test_howto_with_tools(self):
        """Test HowTo with tool list."""
        schema = self.generator.generate(
            schema_type="HowTo",
            content="How to Fix a Bike",
            name="How to Fix a Bike",
            tool=["Wrench", "Screwdriver", "Bike pump"],
            steps=[{"text": "Remove wheel"}]
        )

        assert "tool" in schema
        assert len(schema["tool"]) == 3
        assert schema["tool"][0] == "Wrench"
        assert schema["tool"][1] == "Screwdriver"
        assert schema["tool"][2] == "Bike pump"

    def test_howto_with_supply(self):
        """Test HowTo with supply list."""
        schema = self.generator.generate(
            schema_type="HowTo",
            content="How to Paint a Wall",
            name="How to Paint a Wall",
            supply=["Paint", "Brush", "Roller", "Tape"],
            steps=[{"text": "Prepare surface"}]
        )

        assert "supply" in schema
        assert len(schema["supply"]) == 4
        assert "Paint" in schema["supply"]
        assert "Brush" in schema["supply"]

    def test_howto_with_image(self):
        """Test HowTo with image."""
        schema = self.generator.generate(
            schema_type="HowTo",
            content="How to Tie a Tie",
            name="How to Tie a Tie",
            image="https://example.com/tie-tutorial.jpg",
            steps=[{"text": "Start with wide end"}]
        )

        assert schema["image"] == "https://example.com/tie-tutorial.jpg"

    def test_howto_with_url(self):
        """Test HowTo with URL."""
        schema = self.generator.generate(
            schema_type="HowTo",
            content="How to Code",
            url="https://example.com/coding-tutorial",
            name="How to Code",
            steps=[{"text": "Learn basics"}]
        )

        assert schema["url"] == "https://example.com/coding-tutorial"

    def test_howto_complex_steps(self):
        """Test HowTo with complex, detailed steps."""
        schema = self.generator.generate(
            schema_type="HowTo",
            content="How to Build a Website",
            name="How to Build a Website",
            steps=[
                {"text": "Choose a domain name and register it with a domain registrar"},
                {"text": "Select a web hosting provider and set up your hosting account"},
                {"text": "Install a content management system like WordPress"},
                {"text": "Design your website layout and choose a theme"},
                {"text": "Add content, pages, and blog posts"},
                {"text": "Test your website on different devices and browsers"},
                {"text": "Launch your website and promote it"}
            ]
        )

        assert len(schema["step"]) == 7
        assert all(step["@type"] == "HowToStep" for step in schema["step"])
        assert schema["step"][0]["text"].startswith("Choose a domain")
        assert schema["step"][6]["text"].startswith("Launch your website")


class TestCourseSchemaStrict:
    """Strict tests for Course schema generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SchemaGenerator()

    def test_course_minimal_required_fields(self):
        """Test Course with only required fields."""
        schema = self.generator.generate(
            schema_type="Course",
            content="Introduction to Python - Learn Python programming from scratch",
            name="Introduction to Python",
            description="Learn Python programming from scratch",
            provider={"name": "Tech Academy"}
        )

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Course"
        assert schema["name"] == "Introduction to Python"
        assert schema["description"] == "Learn Python programming from scratch"
        assert schema["provider"]["@type"] == "Organization"
        assert schema["provider"]["name"] == "Tech Academy"

    def test_course_with_url(self):
        """Test Course with URL."""
        schema = self.generator.generate(
            schema_type="Course",
            content="Web Development - Full stack web development course",
            url="https://example.com/courses/web-dev",
            name="Web Development",
            description="Full stack web development course",
            provider={"name": "Code School"}
        )

        assert schema["url"] == "https://example.com/courses/web-dev"

    def test_course_with_course_code(self):
        """Test Course with courseCode."""
        schema = self.generator.generate(
            schema_type="Course",
            content="Data Science 101 - Introduction to data science",
            name="Data Science 101",
            description="Introduction to data science",
            provider={"name": "University"},
            courseCode="DS101"
        )

        assert schema["courseCode"] == "DS101"

    def test_course_with_offers(self):
        """Test Course with pricing offers."""
        schema = self.generator.generate(
            schema_type="Course",
            content="Machine Learning - Advanced ML course",
            name="Machine Learning",
            description="Advanced ML course",
            provider={"name": "AI Institute"},
            offers={
                "price": "499.00",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            }
        )

        assert "offers" in schema
        assert schema["offers"]["@type"] == "Offer"
        assert schema["offers"]["price"] == "499.00"
        assert schema["offers"]["priceCurrency"] == "USD"

    def test_course_with_has_course_instance(self):
        """Test Course with hasCourseInstance."""
        schema = self.generator.generate(
            schema_type="Course",
            content="JavaScript Basics - Learn JavaScript",
            name="JavaScript Basics",
            description="Learn JavaScript",
            provider={"name": "Web Academy"},
            hasCourseInstance={
                "courseMode": "online",
                "startDate": "2024-01-15",
                "endDate": "2024-03-15"
            }
        )

        assert "hasCourseInstance" in schema
        assert schema["hasCourseInstance"]["@type"] == "CourseInstance"
        assert schema["hasCourseInstance"]["courseMode"] == "online"
        assert schema["hasCourseInstance"]["startDate"] == "2024-01-15"

    def test_course_with_instructor(self):
        """Test Course with instructor."""
        schema = self.generator.generate(
            schema_type="Course",
            content="Advanced Python - Expert-level Python",
            name="Advanced Python",
            description="Expert-level Python",
            provider={"name": "Tech University"},
            instructor={"name": "Dr. Jane Smith"}
        )

        assert "instructor" in schema
        assert schema["instructor"]["@type"] == "Person"
        assert schema["instructor"]["name"] == "Dr. Jane Smith"

    def test_course_with_image(self):
        """Test Course with course image."""
        schema = self.generator.generate(
            schema_type="Course",
            content="Photography 101 - Learn photography basics",
            name="Photography 101",
            description="Learn photography basics",
            provider={"name": "Art School"},
            image="https://example.com/photography-course.jpg"
        )

        assert schema["image"] == "https://example.com/photography-course.jpg"

    def test_course_complex_provider(self):
        """Test Course with complex provider organization."""
        schema = self.generator.generate(
            schema_type="Course",
            content="Business Management - MBA-level business course",
            name="Business Management",
            description="MBA-level business course",
            provider={
                "name": "Harvard Business School",
                "url": "https://www.hbs.edu",
                "logo": "https://www.hbs.edu/logo.png"
            }
        )

        assert schema["provider"]["name"] == "Harvard Business School"
        assert schema["provider"]["url"] == "https://www.hbs.edu"
        assert schema["provider"]["logo"] == "https://www.hbs.edu/logo.png"

