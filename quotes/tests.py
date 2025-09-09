from django.test import TestCase
from django.core.exceptions import ValidationError

from .forms import QuoteForm
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


class QuoteFormTests(TestCase):
    def setUp(self):
        Quote.objects.create(text="Existing quote", source="Test Movie", weight=1)

    def test_valid_form(self):
        """Test valid form submission"""
        form_data = {
            'text': 'New quote',
            'source': 'New Movie',
            'weight': 2
        }
        form = QuoteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_duplicate_validation(self):
        """Test form validation for duplicates"""
        form_data = {
            'text': 'Existing quote',
            'source': 'Test Movie',
            'weight': 1
        }
        form = QuoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('This quote from the same source already exists', str(form.errors))

    def test_max_quotes_per_source_validation(self):
        """Test form validation for max quotes per source"""
        # Create 2 more quotes for Test Movie (total 3)
        Quote.objects.create(text="Quote 2", source="Test Movie", weight=1)
        Quote.objects.create(text="Quote 3", source="Test Movie", weight=1)

        form_data = {
            'text': 'Quote 4',
            'source': 'Test Movie',
            'weight': 1
        }
        form = QuoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('A single source cannot have more than 3 quotes', str(form.errors))
