from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


# ========================================================================================================

class User(AbstractUser):
    class Role(models.IntegerChoices):
        CUSTOMER = 1, _("Customer")
        ADMIN = 2, _("Admin")
        SUPERUSER = 3, _("Superuser")

    role = models.IntegerField(choices=Role.choices, default=Role.CUSTOMER)

    def __str__(self):
        return f"{self.username} {self.email}"

 # =======================================================================================================
