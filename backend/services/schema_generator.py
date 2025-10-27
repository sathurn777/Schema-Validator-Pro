"""
Schema Generator Service - Schema Validator Pro
Generates Schema.org JSON-LD markup for 9 content types.

Supported Types:
- Article, Product, Organization, Event, Person
- Recipe, FAQPage, HowTo, Course
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re


class SchemaGenerator:
    """
    Schema.org generator with support for 9 schema types.
    Provides SEO-optimized structured data markup with nested objects and field normalization.
    """

    # ISO4217 currency codes (common subset)
    VALID_CURRENCIES = {
        "USD", "EUR", "GBP", "JPY", "CNY", "AUD", "CAD", "CHF", "HKD", "SGD",
        "SEK", "NOK", "DKK", "NZD", "KRW", "INR", "BRL", "RUB", "ZAR", "MXN"
    }

    # BCP47 language tags (common subset)
    VALID_LANGUAGES = {
        "en", "en-US", "en-GB", "zh", "zh-CN", "zh-TW", "ja", "ko", "fr", "de",
        "es", "it", "pt", "ru", "ar", "hi", "th", "vi", "id", "ms"
    }

    # Schema.org templates with required and optional fields
    SCHEMA_TEMPLATES = {
        "Article": {
            "required": ["headline", "author"],
            "optional": ["description", "image", "publisher", "dateModified", "articleBody", "datePublished"],
        },
        "Product": {
            "required": ["name", "description"],
            "optional": ["brand", "offers", "image", "review", "aggregateRating", "sku"],
        },
        "Organization": {
            "required": ["name"],
            "optional": ["url", "logo", "description", "address", "contactPoint"],
        },
        "Event": {
            "required": ["name", "startDate", "location"],
            "optional": [
                "endDate", "description", "image", "organizer",
                "performer", "offers", "eventStatus", "eventAttendanceMode",
            ],
        },
        "Person": {
            "required": ["name"],
            "optional": [
                "jobTitle", "worksFor", "url", "image", "sameAs",
                "alumniOf", "birthDate", "email", "telephone", "address",
            ],
        },
        "Recipe": {
            "required": ["name", "recipeIngredient", "recipeInstructions"],
            "optional": [
                "image", "author", "datePublished", "description",
                "prepTime", "cookTime", "totalTime", "recipeYield",
                "recipeCategory", "recipeCuisine", "nutrition",
                "aggregateRating", "keywords",
            ],
        },
        "FAQPage": {
            "required": ["mainEntity"],
            "optional": ["about", "description", "name"],
        },
        "HowTo": {
            "required": ["name", "step"],
            "optional": [
                "description", "image", "totalTime",
                "estimatedCost", "supply", "tool", "video",
            ],
        },
        "Course": {
            "required": ["name", "description", "provider"],
            "optional": [
                "url", "courseCode", "hasCourseInstance", "offers",
                "aggregateRating", "review", "educationalLevel",
                "timeRequired", "inLanguage",
            ],
        },
    }

    def __init__(self, site_defaults: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema generator with optional site-level defaults.

        Args:
            site_defaults: Site-level default metadata, e.g.:
                {
                    "publisher_name": "My News Site",
                    "publisher_logo": "https://example.com/logo.png",
                    "brand_name": "My Brand",
                    "sameAs": ["https://twitter.com/mysite"],
                    "inLanguage": "en-US"
                }
        """
        self.supported_types = set(self.SCHEMA_TEMPLATES.keys())
        self.site_defaults = site_defaults or {}

    def generate(
        self, schema_type: str, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate Schema.org JSON-LD for the specified type.

        Args:
            schema_type: Type of schema (Article, Product, etc.)
            content: Main content text to extract data from
            url: Optional URL for the content
            **kwargs: Additional fields specific to the schema type

        Returns:
            Dict containing the Schema.org JSON-LD structure

        Raises:
            ValueError: If schema_type is not supported
        """
        if schema_type not in self.supported_types:
            raise ValueError(
                f"Unsupported schema type: {schema_type}. "
                f"Supported types: {', '.join(sorted(self.supported_types))}"
            )

        # Generate schema based on type
        generators = {
            "Article": self._generate_article,
            "Product": self._generate_product,
            "Organization": self._generate_organization,
            "Event": self._generate_event,
            "Person": self._generate_person,
            "Recipe": self._generate_recipe,
            "FAQPage": self._generate_faq,
            "HowTo": self._generate_howto,
            "Course": self._generate_course,
        }

        generator_func = generators.get(schema_type)
        if generator_func:
            return generator_func(content, url, **kwargs)
        else:
            return self._generate_basic(schema_type, content, url, **kwargs)

    def _generate_article(
        self, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate Article schema with nested objects and normalization."""
        lines = content.split("\n")
        headline = lines[0][:120] if lines else "Article"

        # Extract article body from content (everything after the headline)
        article_body = "\n".join(lines[1:]).strip() if len(lines) > 1 else content

        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": kwargs.get("headline", headline),
        }

        # Add author (Person type)
        if "author" in kwargs:
            author_data = kwargs["author"]
            if isinstance(author_data, str):
                schema["author"] = {"@type": "Person", "name": author_data}
            elif isinstance(author_data, dict):
                schema["author"] = {"@type": "Person", **author_data}
        else:
            schema["author"] = {"@type": "Person", "name": "Unknown"}

        # Add dates (normalized to ISO8601)
        schema["datePublished"] = self._normalize_date(
            kwargs.get("datePublished", datetime.now())
        )
        if "dateModified" in kwargs:
            schema["dateModified"] = self._normalize_date(kwargs["dateModified"])

        # Add publisher (Organization type with logo)
        publisher_name = self._get_default("publisher_name", kwargs)
        publisher_logo = self._get_default("publisher_logo", kwargs)
        if publisher_name:
            schema["publisher"] = {
                "@type": "Organization",
                "name": publisher_name
            }
            if publisher_logo:
                schema["publisher"]["logo"] = {
                    "@type": "ImageObject",
                    "url": self._normalize_url(publisher_logo, url)
                }

        # Add image (ImageObject or array of ImageObjects)
        if "image" in kwargs:
            images = kwargs["image"] if isinstance(kwargs["image"], list) else [kwargs["image"]]
            schema["image"] = [
                {"@type": "ImageObject", "url": self._normalize_url(img, url)}
                if isinstance(img, str) else img
                for img in images
            ]

        # Add optional fields
        if url:
            schema["url"] = self._normalize_url(url)
        if "description" in kwargs:
            schema["description"] = kwargs["description"]

        # Add articleBody - use provided value or extract from content
        if "articleBody" in kwargs:
            schema["articleBody"] = kwargs["articleBody"]
        elif article_body:
            schema["articleBody"] = article_body

        if "wordCount" in kwargs:
            schema["wordCount"] = kwargs["wordCount"]
        if "mainEntityOfPage" in kwargs:
            schema["mainEntityOfPage"] = kwargs["mainEntityOfPage"]

        return schema

    def _generate_product(
        self, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate Product schema with nested objects and normalization."""
        lines = content.split("\n")
        name = lines[0][:120] if lines else "Product"
        description = lines[1] if len(lines) > 1 else "Product description"

        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": kwargs.get("name", name),
            "description": kwargs.get("description", description),
        }

        # Add URL (normalized)
        if url:
            schema["url"] = self._normalize_url(url)

        # Add brand (Brand or Organization type)
        brand_data = self._get_default("brand_name", kwargs)
        if brand_data:
            if isinstance(brand_data, str):
                schema["brand"] = {"@type": "Brand", "name": brand_data}
            elif isinstance(brand_data, dict):
                schema["brand"] = {"@type": "Brand", **brand_data}

        # Add image (ImageObject or array)
        if "image" in kwargs:
            images = kwargs["image"] if isinstance(kwargs["image"], list) else [kwargs["image"]]
            schema["image"] = [
                {"@type": "ImageObject", "url": self._normalize_url(img, url)}
                if isinstance(img, str) else img
                for img in images
            ]

        # Add SKU and GTIN
        if "sku" in kwargs:
            schema["sku"] = kwargs["sku"]
        if "gtin13" in kwargs:
            schema["gtin13"] = kwargs["gtin13"]
        if "mpn" in kwargs:
            schema["mpn"] = kwargs["mpn"]

        # Add offers (Offer type with price/currency/availability)
        if "offers" in kwargs:
            offers_data = kwargs["offers"]
            if isinstance(offers_data, dict):
                schema["offers"] = {
                    "@type": "Offer",
                    "price": offers_data.get("price"),
                    "priceCurrency": self._normalize_currency(offers_data.get("priceCurrency", "USD")),
                    "availability": offers_data.get("availability", "https://schema.org/InStock"),
                    "url": self._normalize_url(offers_data.get("url", url), url) if offers_data.get("url") or url else None
                }
                # Remove None values
                schema["offers"] = {k: v for k, v in schema["offers"].items() if v is not None}
            else:
                schema["offers"] = offers_data

        # Add aggregateRating (AggregateRating type)
        if "aggregateRating" in kwargs:
            rating_data = kwargs["aggregateRating"]
            if isinstance(rating_data, dict):
                schema["aggregateRating"] = {
                    "@type": "AggregateRating",
                    "ratingValue": rating_data.get("ratingValue"),
                    "reviewCount": rating_data.get("reviewCount"),
                    "bestRating": rating_data.get("bestRating", 5),
                    "worstRating": rating_data.get("worstRating", 1)
                }
                # Remove None values
                schema["aggregateRating"] = {k: v for k, v in schema["aggregateRating"].items() if v is not None}
            else:
                schema["aggregateRating"] = rating_data

        # Add manufacturer
        if "manufacturer" in kwargs:
            manufacturer_data = kwargs["manufacturer"]
            if isinstance(manufacturer_data, str):
                schema["manufacturer"] = {"@type": "Organization", "name": manufacturer_data}
            elif isinstance(manufacturer_data, dict):
                schema["manufacturer"] = {"@type": "Organization", **manufacturer_data}

        return schema

    def _generate_organization(
        self, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate Organization schema with structured address and contact."""
        lines = content.split("\n")
        name = lines[0][:120] if lines else "Organization"

        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": kwargs.get("name", name),
        }

        # Add URL (normalized)
        if url:
            schema["url"] = self._normalize_url(url)

        # Add logo (ImageObject)
        if "logo" in kwargs:
            logo_data = kwargs["logo"]
            if isinstance(logo_data, str):
                schema["logo"] = {
                    "@type": "ImageObject",
                    "url": self._normalize_url(logo_data, url)
                }
            else:
                schema["logo"] = logo_data

        # Add description
        if "description" in kwargs:
            schema["description"] = kwargs["description"]

        # Add address (PostalAddress)
        if "address" in kwargs:
            addr_data = kwargs["address"]
            if isinstance(addr_data, str):
                schema["address"] = {
                    "@type": "PostalAddress",
                    "streetAddress": addr_data
                }
            elif isinstance(addr_data, dict):
                schema["address"] = {
                    "@type": "PostalAddress",
                    **addr_data
                }

        # Add contactPoint (ContactPoint)
        if "contactPoint" in kwargs:
            contact_data = kwargs["contactPoint"]
            if isinstance(contact_data, dict):
                schema["contactPoint"] = {
                    "@type": "ContactPoint",
                    **contact_data
                }
            else:
                schema["contactPoint"] = contact_data

        # Add sameAs (social media links)
        if "sameAs" in kwargs:
            schema["sameAs"] = kwargs["sameAs"]

        # Add foundingDate (normalized)
        if "foundingDate" in kwargs:
            schema["foundingDate"] = self._normalize_date(kwargs["foundingDate"])

        return schema

    def _generate_event(
        self, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate Event schema with structured location and organizer."""
        lines = content.split("\n")
        name = lines[0][:120] if lines else "Event"

        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": kwargs.get("name", name),
        }

        # Required: startDate (normalized)
        schema["startDate"] = self._normalize_date(
            kwargs.get("startDate", datetime.now())
        )

        # Required: location (Place with PostalAddress)
        if "location" in kwargs:
            location_data = kwargs["location"]
            if isinstance(location_data, dict):
                schema["location"] = {
                    "@type": "Place",
                    "name": location_data.get("name", "TBD"),
                }
                # Add address as PostalAddress if provided
                if "address" in location_data:
                    addr = location_data["address"]
                    if isinstance(addr, str):
                        schema["location"]["address"] = {
                            "@type": "PostalAddress",
                            "streetAddress": addr
                        }
                    elif isinstance(addr, dict):
                        schema["location"]["address"] = {
                            "@type": "PostalAddress",
                            **addr
                        }
            else:
                schema["location"] = location_data
        else:
            schema["location"] = {
                "@type": "Place",
                "name": kwargs.get("locationName", "TBD"),
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": kwargs.get("locationAddress", "TBD")
                }
            }

        # Add URL (normalized)
        if url:
            schema["url"] = self._normalize_url(url)

        # Add endDate (normalized)
        if "endDate" in kwargs:
            schema["endDate"] = self._normalize_date(kwargs["endDate"])

        # Add description
        if "description" in kwargs:
            schema["description"] = kwargs["description"]

        # Add image (ImageObject or array)
        if "image" in kwargs:
            images = kwargs["image"] if isinstance(kwargs["image"], list) else [kwargs["image"]]
            schema["image"] = [
                {"@type": "ImageObject", "url": self._normalize_url(img, url)}
                if isinstance(img, str) else img
                for img in images
            ]

        # Add organizer (Organization or Person)
        if "organizer" in kwargs:
            organizer_data = kwargs["organizer"]
            if isinstance(organizer_data, str):
                schema["organizer"] = {"@type": "Organization", "name": organizer_data}
            elif isinstance(organizer_data, dict):
                org_type = organizer_data.get("@type", "Organization")
                schema["organizer"] = {"@type": org_type, **organizer_data}

        # Add performer
        if "performer" in kwargs:
            performer_data = kwargs["performer"]
            if isinstance(performer_data, str):
                schema["performer"] = {"@type": "Person", "name": performer_data}
            elif isinstance(performer_data, dict):
                perf_type = performer_data.get("@type", "Person")
                schema["performer"] = {"@type": perf_type, **performer_data}

        # Add offers
        if "offers" in kwargs:
            schema["offers"] = kwargs["offers"]

        # Add eventStatus
        if "eventStatus" in kwargs:
            schema["eventStatus"] = kwargs["eventStatus"]
        else:
            schema["eventStatus"] = "https://schema.org/EventScheduled"

        # Add eventAttendanceMode
        if "eventAttendanceMode" in kwargs:
            schema["eventAttendanceMode"] = kwargs["eventAttendanceMode"]

        return schema

    def _generate_person(
        self, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate Person schema with structured address and organization."""
        lines = content.split("\n")
        name = lines[0][:120] if lines else "Person"

        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": kwargs.get("name", name),
        }

        # Add URL (normalized) - check both url parameter and kwargs
        if url:
            schema["url"] = self._normalize_url(url)
        elif "url" in kwargs:
            schema["url"] = self._normalize_url(kwargs["url"])

        # Add jobTitle
        if "jobTitle" in kwargs:
            schema["jobTitle"] = kwargs["jobTitle"]

        # Add worksFor (Organization)
        if "worksFor" in kwargs:
            works_data = kwargs["worksFor"]
            if isinstance(works_data, str):
                schema["worksFor"] = {"@type": "Organization", "name": works_data}
            elif isinstance(works_data, dict):
                schema["worksFor"] = {"@type": "Organization", **works_data}

        # Add image (ImageObject or URL)
        if "image" in kwargs:
            img_data = kwargs["image"]
            if isinstance(img_data, str):
                schema["image"] = {
                    "@type": "ImageObject",
                    "url": self._normalize_url(img_data, url)
                }
            else:
                schema["image"] = img_data

        # Add sameAs (social media links)
        if "sameAs" in kwargs:
            schema["sameAs"] = kwargs["sameAs"]

        # Add alumniOf
        if "alumniOf" in kwargs:
            alumni_data = kwargs["alumniOf"]
            if isinstance(alumni_data, str):
                schema["alumniOf"] = {"@type": "Organization", "name": alumni_data}
            elif isinstance(alumni_data, dict):
                schema["alumniOf"] = {"@type": "Organization", **alumni_data}

        # Add birthDate (normalized)
        if "birthDate" in kwargs:
            schema["birthDate"] = self._normalize_date(kwargs["birthDate"])

        # Add contact info
        if "email" in kwargs:
            schema["email"] = kwargs["email"]
        if "telephone" in kwargs:
            schema["telephone"] = kwargs["telephone"]

        # Add address (PostalAddress)
        if "address" in kwargs:
            addr_data = kwargs["address"]
            if isinstance(addr_data, str):
                schema["address"] = {
                    "@type": "PostalAddress",
                    "streetAddress": addr_data
                }
            elif isinstance(addr_data, dict):
                schema["address"] = {
                    "@type": "PostalAddress",
                    **addr_data
                }

        return schema

    def _generate_recipe(
        self, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate Recipe schema with HowToStep instructions and nutrition information."""
        lines = content.split("\n")
        name = lines[0][:120] if lines else "Recipe"

        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": kwargs.get("name", name),
        }

        # Required: recipeIngredient
        schema["recipeIngredient"] = kwargs.get("recipeIngredient", ["Ingredients TBD"])

        # Required: recipeInstructions (structured as HowToStep array)
        if "recipeInstructions" in kwargs:
            instructions = kwargs["recipeInstructions"]
            if isinstance(instructions, str):
                # Split by newlines into steps
                steps = [s.strip() for s in instructions.split("\n") if s.strip()]
                schema["recipeInstructions"] = [
                    {
                        "@type": "HowToStep",
                        "text": step,
                        "name": f"Step {i+1}",
                        "position": i+1
                    }
                    for i, step in enumerate(steps)
                ]
            elif isinstance(instructions, list):
                # Convert list to HowToStep array
                schema["recipeInstructions"] = [
                    {
                        "@type": "HowToStep",
                        "text": step if isinstance(step, str) else step.get("text", ""),
                        "name": step.get("name", f"Step {i+1}") if isinstance(step, dict) else f"Step {i+1}",
                        "position": i+1
                    }
                    for i, step in enumerate(instructions)
                ]
            else:
                schema["recipeInstructions"] = instructions
        else:
            schema["recipeInstructions"] = [{"@type": "HowToStep", "text": "Instructions TBD", "position": 1}]

        # Add author (Person type)
        if "author" in kwargs:
            author_data = kwargs["author"]
            if isinstance(author_data, str):
                schema["author"] = {"@type": "Person", "name": author_data}
            elif isinstance(author_data, dict):
                schema["author"] = {"@type": "Person", **author_data}

        # Add nutrition (NutritionInformation type)
        if "nutrition" in kwargs:
            nutrition_data = kwargs["nutrition"]
            if isinstance(nutrition_data, dict):
                schema["nutrition"] = {
                    "@type": "NutritionInformation",
                    **nutrition_data
                }
            else:
                schema["nutrition"] = nutrition_data

        # Add image (ImageObject or array)
        if "image" in kwargs:
            images = kwargs["image"] if isinstance(kwargs["image"], list) else [kwargs["image"]]
            schema["image"] = [
                {"@type": "ImageObject", "url": self._normalize_url(img, url)}
                if isinstance(img, str) else img
                for img in images
            ]

        # Add other optional fields
        if url:
            schema["url"] = self._normalize_url(url)
        if "datePublished" in kwargs:
            schema["datePublished"] = self._normalize_date(kwargs["datePublished"])
        if "description" in kwargs:
            schema["description"] = kwargs["description"]
        if "prepTime" in kwargs:
            schema["prepTime"] = kwargs["prepTime"]
        if "cookTime" in kwargs:
            schema["cookTime"] = kwargs["cookTime"]
        if "totalTime" in kwargs:
            schema["totalTime"] = kwargs["totalTime"]
        if "recipeYield" in kwargs:
            schema["recipeYield"] = kwargs["recipeYield"]
        if "recipeCategory" in kwargs:
            schema["recipeCategory"] = kwargs["recipeCategory"]
        if "recipeCuisine" in kwargs:
            schema["recipeCuisine"] = kwargs["recipeCuisine"]
        if "cookingMethod" in kwargs:
            schema["cookingMethod"] = kwargs["cookingMethod"]
        if "keywords" in kwargs:
            schema["keywords"] = kwargs["keywords"]
        if "aggregateRating" in kwargs:
            rating_data = kwargs["aggregateRating"]
            if isinstance(rating_data, dict):
                schema["aggregateRating"] = {
                    "@type": "AggregateRating",
                    **rating_data
                }
            else:
                schema["aggregateRating"] = rating_data

        return schema

    def _generate_faq(
        self, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate FAQPage schema with Q&A structure."""
        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
        }

        # Handle mainEntity (required) - list of Question objects
        if "mainEntity" in kwargs:
            schema["mainEntity"] = kwargs["mainEntity"]
        elif "questions" in kwargs:
            # Support questions parameter (list of {question, answer} dicts)
            questions_list = kwargs["questions"]
            if questions_list:
                schema["mainEntity"] = [
                    {
                        "@type": "Question",
                        "name": q.get("question", ""),
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": q.get("answer", "")
                        }
                    }
                    for q in questions_list
                ]
            else:
                schema["mainEntity"] = []
        else:
            # Parse content to extract Q&A pairs
            questions: List[Dict[str, Any]] = []
            lines = content.split("\n")
            current_question: Optional[str] = None
            current_answer: List[str] = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect questions (lines ending with ?)
                if line.endswith("?") or line.lower().startswith("q:"):
                    if current_question is not None and current_answer:
                        questions.append({
                            "@type": "Question",
                            "name": current_question,
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": " ".join(current_answer)
                            }
                        })
                    current_question = line.replace("Q:", "").replace("q:", "").strip()
                    current_answer = []
                elif current_question is not None:
                    answer_text = line.replace("A:", "").replace("a:", "").strip()
                    if answer_text:
                        current_answer.append(answer_text)

            # Add last Q&A pair
            if current_question is not None and current_answer:
                questions.append({
                    "@type": "Question",
                    "name": current_question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": " ".join(current_answer)
                    }
                })

            schema["mainEntity"] = questions if questions else [{
                "@type": "Question",
                "name": "Sample Question",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Sample Answer"
                }
            }]

        # Add optional fields
        if url:
            schema["url"] = url
        for field in ["about", "description", "name"]:
            if field in kwargs:
                schema[field] = kwargs[field]

        return schema

    def _generate_howto(
        self, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate HowTo schema with step-by-step format."""
        lines = content.split("\n")
        name = lines[0][:120] if lines else "How-To Guide"

        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": kwargs.get("name", name),
        }

        # Handle step (required) - list of HowToStep objects
        if "step" in kwargs:
            schema["step"] = kwargs["step"]
        elif "steps" in kwargs:
            # Support steps parameter (list of {text} dicts or strings)
            steps_list = kwargs["steps"]
            if steps_list:
                schema["step"] = [
                    {
                        "@type": "HowToStep",
                        "position": i + 1,
                        "text": step.get("text", step) if isinstance(step, dict) else step,
                        "name": step.get("name", f"Step {i + 1}") if isinstance(step, dict) else f"Step {i + 1}",
                    }
                    for i, step in enumerate(steps_list)
                ]
            else:
                schema["step"] = []
        else:
            # Parse content to extract steps
            steps = []
            step_number = 1

            for line in lines[1:]:  # Skip first line (name)
                line = line.strip()
                if not line:
                    continue

                # Detect steps (numbered or starting with "Step")
                if (re.match(r'^\d+[\.\)]\s', line) or
                    line.lower().startswith("step")):
                    # Clean step text
                    step_text = re.sub(r'^\d+[\.\)]\s', '', line)
                    step_text = re.sub(r'^step\s*\d*:?\s*', '', step_text, flags=re.IGNORECASE)

                    if step_text:
                        steps.append({
                            "@type": "HowToStep",
                            "position": step_number,
                            "text": step_text,
                            "name": f"Step {step_number}",
                        })
                        step_number += 1

            schema["step"] = steps if steps else [{
                "@type": "HowToStep",
                "position": 1,
                "text": "Follow the instructions",
                "name": "Step 1",
            }]

        # Add URL if provided
        if url:
            schema["url"] = url

        # Add optional fields
        optional_fields = ["description", "image", "totalTime", "estimatedCost", "supply", "tool", "video"]
        for field in optional_fields:
            if field in kwargs:
                schema[field] = kwargs[field]

        return schema

    def _generate_course(
        self, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate Course schema with educational metadata."""
        lines = content.split("\n")
        name = lines[0][:120] if lines else "Course"
        description = lines[1] if len(lines) > 1 else "Educational course"

        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Course",
            "name": kwargs.get("name", name),
            "description": kwargs.get("description", description),
        }

        # Handle provider (required)
        if "provider" in kwargs:
            provider_data = kwargs["provider"]
            if isinstance(provider_data, dict):
                schema["provider"] = {
                    "@type": "Organization",
                    **provider_data
                }
            else:
                schema["provider"] = provider_data
        else:
            schema["provider"] = {
                "@type": "Organization",
                "name": "Educational Institution"
            }

        # Handle instructor (optional)
        if "instructor" in kwargs:
            instructor_data = kwargs["instructor"]
            if isinstance(instructor_data, dict):
                schema["instructor"] = {
                    "@type": "Person",
                    **instructor_data
                }
            else:
                schema["instructor"] = instructor_data

        # Handle offers (optional)
        if "offers" in kwargs:
            offers_data = kwargs["offers"]
            if isinstance(offers_data, dict):
                schema["offers"] = {
                    "@type": "Offer",
                    **offers_data
                }
            else:
                schema["offers"] = offers_data

        # Handle hasCourseInstance (optional)
        if "hasCourseInstance" in kwargs:
            instance_data = kwargs["hasCourseInstance"]
            if isinstance(instance_data, dict):
                schema["hasCourseInstance"] = {
                    "@type": "CourseInstance",
                    **instance_data
                }
            else:
                schema["hasCourseInstance"] = instance_data

        # Add URL if provided
        if url:
            schema["url"] = url

        # Add other optional fields
        optional_fields = [
            "courseCode", "image",
            "aggregateRating", "review", "educationalLevel",
            "timeRequired", "inLanguage"
        ]
        for field in optional_fields:
            if field in kwargs:
                schema[field] = kwargs[field]

        return schema

    def _generate_basic(
        self, schema_type: str, content: str, url: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate basic schema for any type (fallback)."""
        lines = content.split("\n")
        name = lines[0][:120] if lines else schema_type

        schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": kwargs.get("name", name),
        }

        if url:
            schema["url"] = url

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in schema and value is not None:
                schema[key] = value

        return schema

    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Validate that a schema has required fields.

        Args:
            schema: The schema dict to validate

        Returns:
            True if valid, False otherwise
        """
        if "@context" not in schema or "@type" not in schema:
            return False

        schema_type = schema.get("@type")
        if schema_type not in self.SCHEMA_TEMPLATES:
            return True  # Unknown types pass validation

        template = self.SCHEMA_TEMPLATES[schema_type]
        required_fields = template.get("required", [])

        # Check all required fields are present
        for field in required_fields:
            if field not in schema:
                return False

        return True

    def get_supported_types(self) -> List[str]:
        """Get list of supported schema types."""
        return sorted(list(self.supported_types))

    def _get_default(self, key: str, kwargs: Dict[str, Any], fallback: Any = None) -> Any:
        """
        Get configuration value with priority: kwargs > site_defaults > fallback.

        Args:
            key: Configuration key
            kwargs: Request-specific kwargs
            fallback: Default value if not found

        Returns:
            Configuration value
        """
        return kwargs.get(key, self.site_defaults.get(key, fallback))

    def _normalize_date(self, value: Any, format: str = "iso8601") -> str:
        """
        Normalize date to ISO8601 format.

        Args:
            value: Date value (datetime, str, or None)
            format: Output format (currently only 'iso8601' supported)

        Returns:
            ISO8601 formatted date string
        """
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, str):
            # Try parsing common formats
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.date().isoformat()
                except ValueError:
                    continue
            # If already ISO8601, return as-is
            if re.match(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?", value):
                return value
        # Fallback to current date
        return datetime.now().date().isoformat()

    def _normalize_url(self, value: str, base_url: Optional[str] = None) -> str:
        """
        Normalize URL to absolute path.

        Args:
            value: URL string
            base_url: Base URL for resolving relative paths

        Returns:
            Absolute URL
        """
        if not value:
            return value

        # If already absolute URL, return as-is
        parsed = urlparse(value)
        if parsed.scheme in ("http", "https"):
            return value

        # If relative path and base_url provided, join them
        if base_url:
            return urljoin(base_url, value)

        # Otherwise return original (may not be valid URL)
        return value

    def _normalize_currency(self, value: str) -> str:
        """
        Validate and normalize ISO4217 currency code.

        Args:
            value: Currency code string

        Returns:
            Uppercase ISO4217 currency code
        """
        if not value:
            return "USD"  # Default to USD

        value_upper = value.upper()
        if value_upper in self.VALID_CURRENCIES:
            return value_upper

        # If not in whitelist, return default
        return "USD"

    def _normalize_language(self, value: str) -> str:
        """
        Validate and normalize BCP47 language tag.

        Args:
            value: Language tag string

        Returns:
            Lowercase BCP47 language tag
        """
        if not value:
            return "en"  # Default to English

        value_lower = value.lower()
        if value_lower in self.VALID_LANGUAGES:
            return value_lower

        # Try matching main language code (e.g., zh-Hans-CN -> zh)
        main_lang = value_lower.split("-")[0]
        if main_lang in self.VALID_LANGUAGES:
            return main_lang

        return "en"

    def get_template(self, schema_type: str) -> Dict[str, Any]:
        """Get the template definition for a schema type."""
        if schema_type not in self.SCHEMA_TEMPLATES:
            raise ValueError(f"Unknown schema type: {schema_type}")
        return self.SCHEMA_TEMPLATES[schema_type].copy()

