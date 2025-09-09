from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

class Quote(models.Model):
    text = models.TextField()
    source = models.CharField(max_length=255)
    weight = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["text", "source"], name="uniq_source_text"),
        ]

    def __str__(self) -> str:
        return f"{self.source}: {self.text[:50]}" if self.text else self.source

    def clean(self) -> None:
        # Enforce max 3 quotes per source
        existing_count = Quote.objects.filter(source=self.source).exclude(pk=self.pk).count()
        if existing_count >= 3:
            raise ValidationError({"source": "A source cannot have more than 3 quotes."})

    def save(self, *args, **kwargs):
        # Ensure model-level validations run on save paths outside forms/admin
        self.full_clean()
        return super().save(*args, **kwargs)
