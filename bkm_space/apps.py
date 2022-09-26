# -*- coding: utf-8 -*-

from django.apps import AppConfig


class BkmSpaceConfig(AppConfig):
    name = "bkm_space"
    verbose_name = "BK Monitor Space"

    def ready(self):
        pass
