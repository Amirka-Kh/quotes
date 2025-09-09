from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.db.models import F

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
