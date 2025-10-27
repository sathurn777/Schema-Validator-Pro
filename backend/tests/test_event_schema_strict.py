"""
Strict Event Schema Generation Tests

This file contains STRICT tests for Event schema generation.
These tests verify ACTUAL functionality, not just code coverage.

Test Philosophy:
- Test real business logic, not syntax
- Verify actual values, not just field existence
- Test all parameter combinations
- Test edge cases and error conditions
- NO mocking of core business logic
"""

import pytest
from datetime import datetime
from backend.services.schema_generator import SchemaGenerator


class TestEventSchemaStartDateGeneration:
    """
    CRITICAL: Test Event startDate generation.
    
    This is a required field for Event schema.
    """

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_event_with_start_date_string(self):
        """Test Event with startDate as string."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Tech Conference 2024",
            startDate="2024-06-15T09:00:00"
        )

        assert "startDate" in schema, "Event MUST have startDate"
        assert "2024-06-15" in schema["startDate"]

    def test_event_with_start_date_datetime(self):
        """Test Event with startDate as datetime object."""
        start = datetime(2024, 12, 25, 18, 0, 0)
        schema = self.generator.generate(
            schema_type="Event",
            content="Christmas Concert",
            startDate=start
        )

        assert "startDate" in schema
        assert "2024-12-25" in schema["startDate"]

    def test_event_without_start_date_has_default(self):
        """Test Event without startDate gets current datetime."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Default Event"
        )

        assert "startDate" in schema
        # Should have a valid date
        assert len(schema["startDate"]) > 0


class TestEventSchemaLocationGeneration:
    """
    CRITICAL: Test Event location generation.
    
    This is a required field for Event schema.
    """

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_event_with_location_dict_full(self):
        """Test Event with location as full dict."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Conference 2024",
            startDate="2024-06-15",
            location={
                "name": "Convention Center",
                "address": {
                    "streetAddress": "123 Main St",
                    "addressLocality": "San Francisco",
                    "addressRegion": "CA",
                    "postalCode": "94102",
                    "addressCountry": "US"
                }
            }
        )

        assert "location" in schema, "Event MUST have location"
        location = schema["location"]
        assert location["@type"] == "Place"
        assert location["name"] == "Convention Center"
        
        # Verify address structure
        address = location["address"]
        assert address["@type"] == "PostalAddress"
        assert address["streetAddress"] == "123 Main St"
        assert address["addressLocality"] == "San Francisco"
        assert address["addressRegion"] == "CA"
        assert address["postalCode"] == "94102"
        assert address["addressCountry"] == "US"

    def test_event_with_location_dict_address_string(self):
        """Test Event with location dict and address as string."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Local Meetup",
            startDate="2024-07-01",
            location={
                "name": "Coffee Shop",
                "address": "456 Oak Avenue, Portland, OR"
            }
        )

        location = schema["location"]
        assert location["@type"] == "Place"
        assert location["name"] == "Coffee Shop"
        
        address = location["address"]
        assert address["@type"] == "PostalAddress"
        assert address["streetAddress"] == "456 Oak Avenue, Portland, OR"

    def test_event_with_location_dict_no_address(self):
        """Test Event with location dict without address."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Online Event",
            startDate="2024-08-01",
            location={
                "name": "Virtual Conference Room"
            }
        )

        location = schema["location"]
        assert location["@type"] == "Place"
        assert location["name"] == "Virtual Conference Room"
        # Address is optional when location is provided

    def test_event_without_location_has_default(self):
        """Test Event without location gets default."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Default Event",
            startDate="2024-09-01"
        )

        assert "location" in schema
        location = schema["location"]
        assert location["@type"] == "Place"
        assert "name" in location

    def test_event_with_location_name_and_address_kwargs(self):
        """Test Event with locationName and locationAddress kwargs."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Community Event",
            startDate="2024-10-01",
            locationName="City Park",
            locationAddress="789 Park Drive"
        )

        location = schema["location"]
        assert location["@type"] == "Place"
        assert location["name"] == "City Park"
        assert location["address"]["streetAddress"] == "789 Park Drive"


class TestEventSchemaEndDateGeneration:
    """Test Event endDate generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_event_with_end_date(self):
        """Test Event with endDate."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Multi-Day Conference",
            startDate="2024-06-15T09:00:00",
            endDate="2024-06-17T17:00:00"
        )

        assert "endDate" in schema
        assert "2024-06-17" in schema["endDate"]

    def test_event_without_end_date(self):
        """Test Event without endDate."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Single Event",
            startDate="2024-06-15"
        )

        # endDate is optional
        assert "endDate" not in schema


class TestEventSchemaOrganizerGeneration:
    """Test Event organizer field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_event_with_organizer_string(self):
        """Test Event with organizer as string."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Tech Meetup",
            startDate="2024-06-15",
            organizer="Tech Community SF"
        )

        assert "organizer" in schema
        organizer = schema["organizer"]
        assert organizer["@type"] == "Organization"
        assert organizer["name"] == "Tech Community SF"

    def test_event_with_organizer_dict_organization(self):
        """Test Event with organizer as Organization dict."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Corporate Event",
            startDate="2024-06-15",
            organizer={
                "@type": "Organization",
                "name": "Acme Corp",
                "url": "https://acme.com"
            }
        )

        organizer = schema["organizer"]
        assert organizer["@type"] == "Organization"
        assert organizer["name"] == "Acme Corp"
        assert organizer["url"] == "https://acme.com"

    def test_event_with_organizer_dict_person(self):
        """Test Event with organizer as Person dict."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Personal Event",
            startDate="2024-06-15",
            organizer={
                "@type": "Person",
                "name": "John Doe"
            }
        )

        organizer = schema["organizer"]
        assert organizer["@type"] == "Person"
        assert organizer["name"] == "John Doe"

    def test_event_without_organizer(self):
        """Test Event without organizer."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Simple Event",
            startDate="2024-06-15"
        )

        # Organizer is optional
        assert "organizer" not in schema


class TestEventSchemaPerformerGeneration:
    """Test Event performer field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_event_with_performer_string(self):
        """Test Event with performer as string."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Concert",
            startDate="2024-06-15",
            performer="The Beatles"
        )

        assert "performer" in schema
        performer = schema["performer"]
        assert performer["@type"] == "Person"
        assert performer["name"] == "The Beatles"

    def test_event_with_performer_dict(self):
        """Test Event with performer as dict."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Music Festival",
            startDate="2024-06-15",
            performer={
                "@type": "MusicGroup",
                "name": "Rock Band",
                "url": "https://rockband.com"
            }
        )

        performer = schema["performer"]
        assert performer["@type"] == "MusicGroup"
        assert performer["name"] == "Rock Band"
        assert performer["url"] == "https://rockband.com"

    def test_event_without_performer(self):
        """Test Event without performer."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Conference",
            startDate="2024-06-15"
        )

        # Performer is optional
        assert "performer" not in schema


class TestEventSchemaOffersGeneration:
    """Test Event offers field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_event_with_offers(self):
        """Test Event with ticket offers."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Paid Conference",
            startDate="2024-06-15",
            offers={
                "@type": "Offer",
                "price": "299.00",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": "https://example.com/tickets"
            }
        )

        assert "offers" in schema
        offers = schema["offers"]
        assert offers["@type"] == "Offer"
        assert offers["price"] == "299.00"
        assert offers["priceCurrency"] == "USD"

    def test_event_without_offers(self):
        """Test Event without offers (free event)."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Free Meetup",
            startDate="2024-06-15"
        )

        # Offers is optional
        assert "offers" not in schema


class TestEventSchemaImageGeneration:
    """Test Event image field generation."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_event_with_single_image(self):
        """Test Event with single image."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Conference 2024",
            startDate="2024-06-15",
            url="https://example.com/event",
            image="conference-banner.jpg"
        )

        assert "image" in schema
        assert isinstance(schema["image"], list)
        assert len(schema["image"]) == 1
        
        image = schema["image"][0]
        assert image["@type"] == "ImageObject"
        assert "conference-banner.jpg" in image["url"]

    def test_event_with_multiple_images(self):
        """Test Event with multiple images."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Festival",
            startDate="2024-06-15",
            url="https://example.com/event",
            image=["banner.jpg", "venue.jpg", "performers.jpg"]
        )

        assert "image" in schema
        assert len(schema["image"]) == 3
        
        for img in schema["image"]:
            assert img["@type"] == "ImageObject"

    def test_event_without_image(self):
        """Test Event without image."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Simple Event",
            startDate="2024-06-15"
        )

        assert "image" not in schema


class TestEventSchemaOptionalFields:
    """Test Event optional fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_event_with_description(self):
        """Test Event with description."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Tech Conference",
            startDate="2024-06-15",
            description="Annual technology conference featuring industry leaders"
        )

        assert schema["description"] == "Annual technology conference featuring industry leaders"

    def test_event_with_event_status(self):
        """Test Event with eventStatus."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Scheduled Event",
            startDate="2024-06-15",
            eventStatus="https://schema.org/EventScheduled"
        )

        assert schema["eventStatus"] == "https://schema.org/EventScheduled"

    def test_event_with_url(self):
        """Test Event with URL."""
        schema = self.generator.generate(
            schema_type="Event",
            content="Online Event",
            startDate="2024-06-15",
            url="https://example.com/events/tech-conf-2024"
        )

        assert schema["url"] == "https://example.com/events/tech-conf-2024"


class TestEventSchemaComplete:
    """Test complete Event schema with all fields."""

    def setup_method(self):
        self.generator = SchemaGenerator()

    def test_event_complete_tech_conference(self):
        """Test complete Event schema for a tech conference."""
        schema = self.generator.generate(
            schema_type="Event",
            content="TechCon 2024 - The Future of AI",
            url="https://example.com/events/techcon-2024",
            name="TechCon 2024: AI Revolution",
            description="Join us for the biggest tech conference of the year",
            startDate="2024-09-15T09:00:00",
            endDate="2024-09-17T18:00:00",
            location={
                "name": "San Francisco Convention Center",
                "address": {
                    "streetAddress": "747 Howard St",
                    "addressLocality": "San Francisco",
                    "addressRegion": "CA",
                    "postalCode": "94103",
                    "addressCountry": "US"
                }
            },
            organizer={
                "@type": "Organization",
                "name": "Tech Events Inc",
                "url": "https://techevents.com"
            },
            performer={
                "@type": "Person",
                "name": "Dr. Jane Smith",
                "jobTitle": "AI Researcher"
            },
            image=["conference-banner.jpg", "venue-photo.jpg"],
            offers={
                "@type": "Offer",
                "price": "499.00",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": "https://example.com/tickets",
                "validFrom": "2024-01-01"
            },
            eventStatus="https://schema.org/EventScheduled"
        )

        # Validate all fields
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "Event"
        assert schema["name"] == "TechCon 2024: AI Revolution"
        assert schema["url"] == "https://example.com/events/techcon-2024"
        assert schema["description"] == "Join us for the biggest tech conference of the year"
        
        # Dates - CRITICAL
        assert "2024-09-15" in schema["startDate"]
        assert "2024-09-17" in schema["endDate"]
        
        # Location - CRITICAL
        location = schema["location"]
        assert location["@type"] == "Place"
        assert location["name"] == "San Francisco Convention Center"
        assert location["address"]["@type"] == "PostalAddress"
        assert location["address"]["streetAddress"] == "747 Howard St"
        assert location["address"]["addressLocality"] == "San Francisco"
        
        # Organizer
        assert schema["organizer"]["@type"] == "Organization"
        assert schema["organizer"]["name"] == "Tech Events Inc"
        
        # Performer
        assert schema["performer"]["@type"] == "Person"
        assert schema["performer"]["name"] == "Dr. Jane Smith"
        
        # Images
        assert len(schema["image"]) == 2
        
        # Offers
        assert schema["offers"]["@type"] == "Offer"
        assert schema["offers"]["price"] == "499.00"
        assert schema["offers"]["priceCurrency"] == "USD"
        
        # Status
        assert schema["eventStatus"] == "https://schema.org/EventScheduled"

