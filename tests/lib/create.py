#! /usr/bin/env python3

from os import getenv
import random
import string
import time
from app.clients.bifrost.admin import BifrostService


async def call_bifrost_service(site_id=None, brand='bluehost'):
    bifrost = BifrostService(brand=brand, logging=True)

    await bifrost.call('site_delete', { 'site_id': site_id })

