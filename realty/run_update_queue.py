# -*- coding: utf-8 -*-

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "realty.settings"

import django

django.setup()

from cian.models import OffersUpdate


if __name__ == '__main__':
    OffersUpdate.update_queue()

