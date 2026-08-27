from django.contrib.auth.models import User
from django.db import models


class SearchHistory(models.Model):
    """
    Stores questions and answers generated
    by the FMT Assistant for each user.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="search_history",
    )

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.question[:50]}"
        )