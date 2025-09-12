from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.db.models import F
from django.utils import timezone

from .forms import QuoteForm
from .models import Quote
from .services import pick_weighted_quote


def add_quote(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("quotes:random"))
    else:
        form = QuoteForm()
    return render(request, "quotes/quote_form.html", {"form": form})


def random_quote(request: HttpRequest) -> HttpResponse:
    quote = pick_weighted_quote()
    if not quote:
        return render(request, "quotes/random.html", {"quote": None})
    Quote.objects.filter(pk=quote.pk).update(views=F("views") + 1)
    quote.refresh_from_db(fields=["views"])  # keep view count fresh if displayed
    return render(request, "quotes/random.html", {"quote": quote})


def like_quote(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    Quote.objects.filter(pk=pk).update(likes=F("likes") + 1)
    return redirect(reverse("quotes:random"))


def dislike_quote(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    Quote.objects.filter(pk=pk).update(dislikes=F("dislikes") + 1)
    return redirect(reverse("quotes:random"))


def edit_quote(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        instance = Quote.objects.get(pk=pk)
    except Quote.DoesNotExist:
        return redirect(reverse("quotes:random"))
    if request.method == "POST":
        form = QuoteForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(reverse("quotes:random"))
    else:
        form = QuoteForm(instance=instance)
    return render(request, "quotes/quote_form.html", {"form": form, "instance": instance})


def popular_quotes(request: HttpRequest) -> HttpResponse:
    qs = Quote.objects.all()
    source = request.GET.get("source")
    if source:
        qs = qs.filter(source=source)
    quotes = qs.order_by("-likes", "-views")[:10]
    return render(request, "quotes/popular.html", {"quotes": quotes, "active_source": source})


def health_check(request: HttpRequest) -> HttpResponse:
    """Health check endpoint for load balancers and monitoring."""
    import json
    from django.db import connection
    from django.core.cache import cache

    health_data = {
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0",
        "database": "connected",
        "cache": "connected"
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_data["database"] = "connected"
    except Exception as e:
        health_data["database"] = f"error: {str(e)}"
        health_data["status"] = "unhealthy"

    # Check cache connection
    try:
        cache.set("health_check", "test", 10)
        cache.get("health_check")
        health_data["cache"] = "connected"
    except Exception as e:
        health_data["cache"] = f"error: {str(e)}"
        health_data["status"] = "unhealthy"

    # Check if we have quotes
    try:
        quote_count = Quote.objects.count()
        health_data["quotes_count"] = quote_count
        if quote_count == 0:
            health_data["status"] = "degraded"
    except Exception as e:
        health_data["quotes_count"] = f"error: {str(e)}"
        health_data["status"] = "unhealthy"

    status_code = 200 if health_data["status"] == "healthy" else 503

    return HttpResponse(
        json.dumps(health_data, indent=2),
        content_type="application/json",
        status=status_code
    )
