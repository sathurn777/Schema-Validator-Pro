"""
Strict Organization and Person Schema Generation Tests

This file contains STRICT tests for Organization and Person schema generation.
These tests verify ACTUAL functionality, not just code coverage.

Test Philosophy:
- Test real business logic, not syntax
- Verify actual values, not just field existence
- Test all parameter combinations
- Test edge cases and error conditions
"""

import pytest
from backend.services.schema_generator import SchemaGenerator


class TestOrganizationSchemaBasic:
    """Test Organization schema basic fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_organization_minimal(self):
        """Test Organization with minimal fields."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Acme Corporation"
        )

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Organization"
        assert schema["name"] == "Acme Corporation"

    def test_organization_with_custom_name(self):
        """Test Organization with custom name."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Default Name",
            name="Custom Corp"
        )

        assert schema["name"] == "Custom Corp"

    def test_organization_with_url(self):
        """Test Organization with URL."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Tech Company",
            url="https://techcompany.com"
        )

        assert schema["url"] == "https://techcompany.com"

    def test_organization_with_description(self):
        """Test Organization with description."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Innovative Startup",
            description="Leading provider of AI solutions"
        )

        assert schema["description"] == "Leading provider of AI solutions"


class TestOrganizationSchemaLogo:
    """Test Organization logo field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_organization_with_logo_string(self):
        """Test Organization with logo as string."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Brand Corp",
            url="https://brand.com",
            logo="logo.png"
        )

        assert "logo" in schema
        logo = schema["logo"]
        assert logo["@type"] == "ImageObject"
        assert "logo.png" in logo["url"]

    def test_organization_with_logo_dict(self):
        """Test Organization with logo as dict."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Brand Corp",
            logo={
                "@type": "ImageObject",
                "url": "https://brand.com/logo.png",
                "width": "600",
                "height": "60"
            }
        )

        logo = schema["logo"]
        assert logo["@type"] == "ImageObject"
        assert logo["url"] == "https://brand.com/logo.png"
        assert logo["width"] == "600"

    def test_organization_without_logo(self):
        """Test Organization without logo."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Simple Org"
        )

        assert "logo" not in schema


class TestOrganizationSchemaAddress:
    """Test Organization address field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_organization_with_address_string(self):
        """Test Organization with address as string."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Local Business",
            address="123 Main Street, San Francisco, CA"
        )

        assert "address" in schema
        address = schema["address"]
        assert address["@type"] == "PostalAddress"
        assert address["streetAddress"] == "123 Main Street, San Francisco, CA"

    def test_organization_with_address_dict(self):
        """Test Organization with address as dict."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Corporate HQ",
            address={
                "streetAddress": "456 Tech Blvd",
                "addressLocality": "San Francisco",
                "addressRegion": "CA",
                "postalCode": "94102",
                "addressCountry": "US"
            }
        )

        address = schema["address"]
        assert address["@type"] == "PostalAddress"
        assert address["streetAddress"] == "456 Tech Blvd"
        assert address["addressLocality"] == "San Francisco"
        assert address["addressRegion"] == "CA"
        assert address["postalCode"] == "94102"
        assert address["addressCountry"] == "US"

    def test_organization_without_address(self):
        """Test Organization without address."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Virtual Company"
        )

        assert "address" not in schema


class TestOrganizationSchemaContactPoint:
    """Test Organization contactPoint field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_organization_with_contact_point(self):
        """Test Organization with contactPoint."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Customer Service Co",
            contactPoint={
                "telephone": "+1-800-555-1234",
                "contactType": "customer service",
                "email": "support@example.com",
                "availableLanguage": ["English", "Spanish"]
            }
        )

        assert "contactPoint" in schema
        contact = schema["contactPoint"]
        assert contact["@type"] == "ContactPoint"
        assert contact["telephone"] == "+1-800-555-1234"
        assert contact["contactType"] == "customer service"
        assert contact["email"] == "support@example.com"

    def test_organization_without_contact_point(self):
        """Test Organization without contactPoint."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Simple Org"
        )

        assert "contactPoint" not in schema


class TestOrganizationSchemaSocialMedia:
    """Test Organization sameAs field for social media."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_organization_with_same_as_list(self):
        """Test Organization with sameAs as list."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Social Media Active Co",
            sameAs=[
                "https://twitter.com/company",
                "https://facebook.com/company",
                "https://linkedin.com/company/company"
            ]
        )

        assert "sameAs" in schema
        assert len(schema["sameAs"]) == 3
        assert "https://twitter.com/company" in schema["sameAs"]

    def test_organization_with_same_as_string(self):
        """Test Organization with sameAs as single string."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Single Link Co",
            sameAs="https://twitter.com/company"
        )

        assert schema["sameAs"] == "https://twitter.com/company"


class TestOrganizationSchemaFoundingDate:
    """Test Organization foundingDate field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_organization_with_founding_date(self):
        """Test Organization with foundingDate."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Established Company",
            foundingDate="1995-03-15"
        )

        assert "foundingDate" in schema
        assert "1995-03-15" in schema["foundingDate"]

    def test_organization_without_founding_date(self):
        """Test Organization without foundingDate."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="New Startup"
        )

        assert "foundingDate" not in schema


class TestPersonSchemaBasic:
    """Test Person schema basic fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_person_minimal(self):
        """Test Person with minimal fields."""
        schema = self.generator.generate(
            schema_type="Person",
            content="John Doe"
        )

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Person"
        assert schema["name"] == "John Doe"

    def test_person_with_custom_name(self):
        """Test Person with custom name."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Default Name",
            name="Jane Smith"
        )

        assert schema["name"] == "Jane Smith"

    def test_person_with_url(self):
        """Test Person with URL."""
        schema = self.generator.generate(
            schema_type="Person",
            content="John Doe",
            url="https://johndoe.com"
        )

        assert schema["url"] == "https://johndoe.com"

    def test_person_with_job_title(self):
        """Test Person with jobTitle."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Jane Smith",
            jobTitle="Software Engineer"
        )

        assert schema["jobTitle"] == "Software Engineer"


class TestPersonSchemaWorksFor:
    """Test Person worksFor field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_person_with_works_for_string(self):
        """Test Person with worksFor as string."""
        schema = self.generator.generate(
            schema_type="Person",
            content="John Doe",
            worksFor="Acme Corporation"
        )

        assert "worksFor" in schema
        works_for = schema["worksFor"]
        assert works_for["@type"] == "Organization"
        assert works_for["name"] == "Acme Corporation"

    def test_person_with_works_for_dict(self):
        """Test Person with worksFor as dict."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Jane Smith",
            worksFor={
                "name": "Tech Corp",
                "url": "https://techcorp.com"
            }
        )

        works_for = schema["worksFor"]
        assert works_for["@type"] == "Organization"
        assert works_for["name"] == "Tech Corp"
        assert works_for["url"] == "https://techcorp.com"

    def test_person_without_works_for(self):
        """Test Person without worksFor."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Freelancer"
        )

        assert "worksFor" not in schema


class TestPersonSchemaImage:
    """Test Person image field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_person_with_image_string(self):
        """Test Person with image as string."""
        schema = self.generator.generate(
            schema_type="Person",
            content="John Doe",
            url="https://johndoe.com",
            image="profile.jpg"
        )

        assert "image" in schema
        image = schema["image"]
        assert image["@type"] == "ImageObject"
        assert "profile.jpg" in image["url"]

    def test_person_with_image_dict(self):
        """Test Person with image as dict."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Jane Smith",
            image={
                "@type": "ImageObject",
                "url": "https://example.com/jane.jpg",
                "width": "400",
                "height": "400"
            }
        )

        image = schema["image"]
        assert image["@type"] == "ImageObject"
        assert image["url"] == "https://example.com/jane.jpg"

    def test_person_without_image(self):
        """Test Person without image."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Anonymous"
        )

        assert "image" not in schema


class TestPersonSchemaSocialMedia:
    """Test Person sameAs field for social media."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_person_with_same_as_list(self):
        """Test Person with sameAs as list."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Social Media Influencer",
            sameAs=[
                "https://twitter.com/johndoe",
                "https://linkedin.com/in/johndoe",
                "https://github.com/johndoe"
            ]
        )

        assert "sameAs" in schema
        assert len(schema["sameAs"]) == 3
        assert "https://twitter.com/johndoe" in schema["sameAs"]

    def test_person_with_same_as_string(self):
        """Test Person with sameAs as single string."""
        schema = self.generator.generate(
            schema_type="Person",
            content="John Doe",
            sameAs="https://twitter.com/johndoe"
        )

        assert schema["sameAs"] == "https://twitter.com/johndoe"


class TestPersonSchemaAlumniOf:
    """Test Person alumniOf field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_person_with_alumni_of_string(self):
        """Test Person with alumniOf as string."""
        schema = self.generator.generate(
            schema_type="Person",
            content="John Doe",
            alumniOf="Stanford University"
        )

        assert "alumniOf" in schema
        alumni = schema["alumniOf"]
        assert alumni["@type"] == "Organization"
        assert alumni["name"] == "Stanford University"

    def test_person_with_alumni_of_dict(self):
        """Test Person with alumniOf as dict."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Jane Smith",
            alumniOf={
                "name": "MIT",
                "url": "https://mit.edu"
            }
        )

        alumni = schema["alumniOf"]
        assert alumni["@type"] == "Organization"
        assert alumni["name"] == "MIT"
        assert alumni["url"] == "https://mit.edu"

    def test_person_without_alumni_of(self):
        """Test Person without alumniOf."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Self-taught Developer"
        )

        assert "alumniOf" not in schema


class TestPersonSchemaContactInfo:
    """Test Person contact information fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_person_with_email(self):
        """Test Person with email."""
        schema = self.generator.generate(
            schema_type="Person",
            content="John Doe",
            email="john.doe@example.com"
        )

        assert schema["email"] == "john.doe@example.com"

    def test_person_with_telephone(self):
        """Test Person with telephone."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Jane Smith",
            telephone="+1-555-123-4567"
        )

        assert schema["telephone"] == "+1-555-123-4567"

    def test_person_with_both_contact_info(self):
        """Test Person with both email and telephone."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Contact Person",
            email="contact@example.com",
            telephone="+1-555-999-8888"
        )

        assert schema["email"] == "contact@example.com"
        assert schema["telephone"] == "+1-555-999-8888"

    def test_person_without_contact_info(self):
        """Test Person without contact info."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Private Person"
        )

        assert "email" not in schema
        assert "telephone" not in schema


class TestPersonSchemaAddress:
    """Test Person address field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_person_with_address_string(self):
        """Test Person with address as string."""
        schema = self.generator.generate(
            schema_type="Person",
            content="John Doe",
            address="789 Residential St, Portland, OR"
        )

        assert "address" in schema
        address = schema["address"]
        assert address["@type"] == "PostalAddress"
        assert address["streetAddress"] == "789 Residential St, Portland, OR"

    def test_person_with_address_dict(self):
        """Test Person with address as dict."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Jane Smith",
            address={
                "streetAddress": "321 Home Ave",
                "addressLocality": "Seattle",
                "addressRegion": "WA",
                "postalCode": "98101",
                "addressCountry": "US"
            }
        )

        address = schema["address"]
        assert address["@type"] == "PostalAddress"
        assert address["streetAddress"] == "321 Home Ave"
        assert address["addressLocality"] == "Seattle"
        assert address["addressRegion"] == "WA"

    def test_person_without_address(self):
        """Test Person without address."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Nomad"
        )

        assert "address" not in schema


class TestPersonSchemaBirthDate:
    """Test Person birthDate field."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_person_with_birth_date(self):
        """Test Person with birthDate."""
        schema = self.generator.generate(
            schema_type="Person",
            content="John Doe",
            birthDate="1985-07-20"
        )

        assert "birthDate" in schema
        assert "1985-07-20" in schema["birthDate"]

    def test_person_without_birth_date(self):
        """Test Person without birthDate."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Private Person"
        )

        assert "birthDate" not in schema


class TestOrganizationPersonSchemaComplete:
    """Test complete Organization and Person schemas."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_organization_complete(self):
        """Test complete Organization schema with all fields."""
        schema = self.generator.generate(
            schema_type="Organization",
            content="Tech Innovations Inc",
            url="https://techinnovations.com",
            name="Tech Innovations Inc.",
            description="Leading provider of innovative technology solutions",
            logo="https://techinnovations.com/logo.png",
            address={
                "streetAddress": "100 Innovation Drive",
                "addressLocality": "San Francisco",
                "addressRegion": "CA",
                "postalCode": "94105",
                "addressCountry": "US"
            },
            contactPoint={
                "telephone": "+1-800-TECH-INN",
                "contactType": "customer service",
                "email": "support@techinnovations.com",
                "availableLanguage": ["English", "Spanish", "Chinese"]
            },
            sameAs=[
                "https://twitter.com/techinnovations",
                "https://facebook.com/techinnovations",
                "https://linkedin.com/company/tech-innovations"
            ],
            foundingDate="2010-05-15"
        )

        # Validate all fields
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Organization"
        assert schema["name"] == "Tech Innovations Inc."
        assert schema["url"] == "https://techinnovations.com"
        assert schema["description"] == "Leading provider of innovative technology solutions"

        # Logo
        assert schema["logo"]["@type"] == "ImageObject"
        assert "logo.png" in schema["logo"]["url"]

        # Address
        assert schema["address"]["@type"] == "PostalAddress"
        assert schema["address"]["streetAddress"] == "100 Innovation Drive"
        assert schema["address"]["addressLocality"] == "San Francisco"

        # Contact Point
        assert schema["contactPoint"]["@type"] == "ContactPoint"
        assert schema["contactPoint"]["telephone"] == "+1-800-TECH-INN"
        assert schema["contactPoint"]["contactType"] == "customer service"

        # Social Media
        assert len(schema["sameAs"]) == 3
        assert "https://twitter.com/techinnovations" in schema["sameAs"]

        # Founding Date
        assert "2010-05-15" in schema["foundingDate"]

    def test_person_complete(self):
        """Test complete Person schema with all fields."""
        schema = self.generator.generate(
            schema_type="Person",
            content="Dr. Jane Smith",
            url="https://janesmith.com",
            name="Dr. Jane Smith",
            jobTitle="Chief Technology Officer",
            worksFor={
                "name": "Tech Innovations Inc",
                "url": "https://techinnovations.com"
            },
            image="https://janesmith.com/profile.jpg",
            sameAs=[
                "https://twitter.com/drjanesmith",
                "https://linkedin.com/in/janesmith",
                "https://github.com/janesmith"
            ],
            alumniOf={
                "name": "Stanford University",
                "url": "https://stanford.edu"
            },
            email="jane.smith@techinnovations.com",
            telephone="+1-555-CTO-JANE",
            address={
                "streetAddress": "456 Executive Lane",
                "addressLocality": "Palo Alto",
                "addressRegion": "CA",
                "postalCode": "94301",
                "addressCountry": "US"
            },
            birthDate="1980-03-25"
        )

        # Validate all fields
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Person"
        assert schema["name"] == "Dr. Jane Smith"
        assert schema["url"] == "https://janesmith.com"
        assert schema["jobTitle"] == "Chief Technology Officer"

        # Works For
        assert schema["worksFor"]["@type"] == "Organization"
        assert schema["worksFor"]["name"] == "Tech Innovations Inc"

        # Image
        assert schema["image"]["@type"] == "ImageObject"
        assert "profile.jpg" in schema["image"]["url"]

        # Social Media
        assert len(schema["sameAs"]) == 3
        assert "https://twitter.com/drjanesmith" in schema["sameAs"]

        # Alumni
        assert schema["alumniOf"]["@type"] == "Organization"
        assert schema["alumniOf"]["name"] == "Stanford University"

        # Contact Info
        assert schema["email"] == "jane.smith@techinnovations.com"
        assert schema["telephone"] == "+1-555-CTO-JANE"

        # Address
        assert schema["address"]["@type"] == "PostalAddress"
        assert schema["address"]["streetAddress"] == "456 Executive Lane"

        # Birth Date
        assert "1980-03-25" in schema["birthDate"]

