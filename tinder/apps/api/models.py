from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    """Stores profile info

    Attributes:
        user: Related User model

    """

    user = models.OneToOneField(
        to=get_user_model(),
        on_delete=models.CASCADE,
    )
    full_name = models.CharField(_("Full name"), max_length=50)
    avatar = models.CharField(_("Profile photo URL"), max_length=500)
    contact = models.CharField(_("User's contact info"), max_length=50)
    about = models.TextField(blank=True)
    latitude = models.DecimalField(decimal_places=7, max_digits=9, default=Decimal("0.0"))
    longitude = models.DecimalField(decimal_places=7, max_digits=9, default=Decimal("0.0"))
    liked = models.ManyToManyField("UserProfile", "liked_by", blank=True)
    disliked = models.ManyToManyField("UserProfile", "disliked_by", blank=True)
    matched = models.ManyToManyField("UserProfile", "matched_related", blank=True)

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return self.full_name
