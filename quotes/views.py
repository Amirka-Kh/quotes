from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import QuoteForm

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
    return render(request, "quotes/random.html")
