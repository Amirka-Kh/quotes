from __future__ import annotations

import random
from typing import Optional

from django.db.models import Sum

from .models import Quote

def pick_weighted_quote() -> Optional[Quote]:
    total_weight = Quote.objects.aggregate(Sum("weight")).get("weight__sum") or 0
    if total_weight <= 0:
        return None
    target = random.randint(1, total_weight)
    cumulative = 0
    for row in Quote.objects.order_by("id").values("id", "weight"):
        cumulative += int(row["weight"]) or 0
        if cumulative >= target:
            try:
                return Quote.objects.get(pk=row["id"])
            # If the quote doesn’t exist anymore (possible race condition: deleted between .values() query and .get()), it skips to the next row.
            except Quote.DoesNotExist:
                continue
    # If failed, return something if possible
    return Quote.objects.order_by("-weight").first()
