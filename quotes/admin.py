from django.contrib import admin

from .models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "short_text", "weight", "views", "likes", "dislikes", "created_at")
    list_filter = ("source",)
    search_fields = ("source", "text")

    def short_text(self, obj: Quote) -> str:
        return (obj.text or "")[:60]
    short_text.short_description = "text"
