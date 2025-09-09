from django import forms
from django.core.exceptions import ValidationError

from .models import Quote

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ["text", "source", "weight"]

    def clean(self):
        cleaned = super().clean()
        text = cleaned.get("text")
        source = cleaned.get("source")
        if text and source:
            exists_qs = Quote.objects.filter(text=text, source=source)
            if self.instance and self.instance.pk:
                exists_qs = exists_qs.exclude(pk=self.instance.pk)
            if exists_qs.exists():
                raise ValidationError("This quote from the same source already exists.")

            count_same_source = Quote.objects.filter(source=source)
            if self.instance and self.instance.pk:
                count_same_source = count_same_source.exclude(pk=self.instance.pk)
            if count_same_source.count() >= 3:
                raise ValidationError("A single source cannot have more than 3 quotes.")
        return cleaned

