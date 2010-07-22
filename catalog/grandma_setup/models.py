# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from grandma.models import BaseSettings

class CatalogSettings(BaseSettings):
    default_models = models.BooleanField(verbose_name=_('Use default settings'),
        default=True)
