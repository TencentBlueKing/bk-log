# -*- coding: utf-8 -*-

from django.apps import AppConfig

from bkm_space.api import load_space_api_class


class BkmSpaceConfig(AppConfig):
    name = "bkm_space"
    verbose_name = "BK Monitor Space"

    def ready(self):
        load_space_api_class()
