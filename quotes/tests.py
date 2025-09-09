from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse

from .forms import QuoteForm
from .models import Quote
from .services import pick_weighted_quote


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


class WeightedSelectionTests(TestCase):
    def setUp(self):
        # Create quotes with different weights
        self.quote1 = Quote.objects.create(text="Quote 1", source="Movie 1", weight=1)
        self.quote2 = Quote.objects.create(text="Quote 2", source="Movie 2", weight=3)
        self.quote3 = Quote.objects.create(text="Quote 3", source="Movie 3", weight=6)

    def test_no_quotes_returns_none(self):
        """Test that function returns None when no quotes exist"""
        Quote.objects.all().delete()
        result = pick_weighted_quote()
        self.assertIsNone(result)

    def test_weighted_selection_bias(self):
        """Test that higher weight quotes are selected more often"""
        # Run many trials to test statistical bias
        results = []
        for _ in range(1000):
            quote = pick_weighted_quote()
            if quote:
                results.append(quote.pk)

        # Count occurrences
        counts = {}
        for pk in results:
            counts[pk] = counts.get(pk, 0) + 1

        # Quote 3 (weight 6) should be selected most often
        # Quote 2 (weight 3) should be selected less often
        # Quote 1 (weight 1) should be selected least often
        self.assertGreater(counts.get(self.quote3.pk, 0), counts.get(self.quote1.pk, 0))
        self.assertGreater(counts.get(self.quote2.pk, 0), counts.get(self.quote1.pk, 0))


class QuoteViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.quote = Quote.objects.create(
            text="Test quote", source="Test Movie", weight=1
        )

    def test_random_quote_view(self):
        """Test random quote view displays quote and increments views"""
        initial_views = self.quote.views
        response = self.client.get(reverse('quotes:random'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test quote")

        # Check that views were incremented
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.views, initial_views + 1)

    def test_random_quote_view_no_quotes(self):
        """Test random quote view when no quotes exist"""
        Quote.objects.all().delete()
        response = self.client.get(reverse('quotes:random'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No quotes available")

    def test_like_quote_view(self):
        """Test like quote view increments likes and redirects"""
        initial_likes = self.quote.likes
        response = self.client.post(reverse('quotes:like', args=[self.quote.pk]))

        self.assertEqual(response.status_code, 302)  # Redirect
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.likes, initial_likes + 1)

    def test_dislike_quote_view(self):
        """Test dislike quote view increments dislikes and redirects"""
        initial_dislikes = self.quote.dislikes
        response = self.client.post(reverse('quotes:dislike', args=[self.quote.pk]))

        self.assertEqual(response.status_code, 302)  # Redirect
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.dislikes, initial_dislikes + 1)

    def test_like_dislike_get_method_fails(self):
        """Test that GET method for like/dislike returns 400"""
        response = self.client.get(reverse('quotes:like', args=[self.quote.pk]))
        self.assertEqual(response.status_code, 400)

        response = self.client.get(reverse('quotes:dislike', args=[self.quote.pk]))
        self.assertEqual(response.status_code, 400)

    def test_popular_quotes_view(self):
        """Test popular quotes view displays quotes ordered by likes"""
        # Create quotes with different like counts
        quote2 = Quote.objects.create(text="Quote 2", source="Movie 2", weight=1, likes=5)
        quote3 = Quote.objects.create(text="Quote 3", source="Movie 3", weight=1, likes=10)

        response = self.client.get(reverse('quotes:popular'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quote 3")  # Highest likes
        self.assertContains(response, "Quote 2")
        self.assertContains(response, "Test quote")

    def test_popular_quotes_view_with_filter(self):
        """Test popular quotes view with source filter"""
        quote2 = Quote.objects.create(text="Quote 2", source="Movie 2", weight=1, likes=5)

        response = self.client.get(reverse('quotes:popular'), {'source': 'Movie 2'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quote 2")
        self.assertNotContains(response, "Test quote")

    def test_add_quote_view_get(self):
        """Test add quote view GET request"""
        response = self.client.get(reverse('quotes:add'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Quote")

    def test_add_quote_view_post_valid(self):
        """Test add quote view POST with valid data"""
        form_data = {
            'text': 'New quote',
            'source': 'New Movie',
            'weight': 2
        }
        response = self.client.post(reverse('quotes:add'), form_data)

        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Quote.objects.filter(text='New quote').exists())

    def test_edit_quote_view_get(self):
        """Test edit quote view GET request"""
        response = self.client.get(reverse('quotes:edit', args=[self.quote.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Quote")
        self.assertContains(response, "Test quote")

    def test_edit_quote_view_post_valid(self):
        """Test edit quote view POST with valid data"""
        form_data = {
            'text': 'Updated quote',
            'source': 'Updated Movie',
            'weight': 3
        }
        response = self.client.post(reverse('quotes:edit', args=[self.quote.pk]), form_data)

        self.assertEqual(response.status_code, 302)  # Redirect
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.text, 'Updated quote')

    def test_edit_quote_view_nonexistent(self):
        """Test edit quote view with nonexistent quote"""
        response = self.client.get(reverse('quotes:edit', args=[999]))

        self.assertEqual(response.status_code, 302)  # Redirect to random
