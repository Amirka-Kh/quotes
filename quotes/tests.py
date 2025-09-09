from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import Quote


class QuoteModelTests(TestCase):
    def setUp(self):
        self.quote1 = Quote.objects.create(
            text="Test quote 1", source="Test Movie", weight=1
        )
        self.quote2 = Quote.objects.create(
            text="Test quote 2", source="Test Movie", weight=2
        )

    def test_quote_creation(self):
        """Test basic quote creation"""
        self.assertEqual(self.quote1.text, "Test quote 1")
        self.assertEqual(self.quote1.source, "Test Movie")
        self.assertEqual(self.quote1.weight, 1)
        self.assertEqual(self.quote1.views, 0)
        self.assertEqual(self.quote1.likes, 0)
        self.assertEqual(self.quote1.dislikes, 0)

    def test_duplicate_prevention(self):
        """Test that duplicate text+source combinations are prevented"""
        with self.assertRaises(ValidationError):
            Quote.objects.create(
                text="Test quote 1", source="Test Movie", weight=1
            )

    def test_max_quotes_per_source(self):
        """Test that max 3 quotes per source is enforced"""
        # Create 1 more quote for the same source (total will be 3)
        Quote.objects.create(text="Test quote 3", source="Test Movie", weight=1)

        # Try to create a 4th quote - should fail validation
        with self.assertRaises(ValidationError):
            Quote.objects.create(text="Test quote 4", source="Test Movie", weight=1)

    def test_weight_validation(self):
        """Test that weight must be positive"""
        quote = Quote(text="Test", source="Test", weight=0)
        with self.assertRaises(ValidationError):
            quote.full_clean()

    def test_str_representation(self):
        """Test string representation of Quote"""
        expected = "Test Movie: Test quote 1"
        self.assertEqual(str(self.quote1), expected)

