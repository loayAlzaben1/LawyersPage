"""Placeholder migration 0003_newsletter

This project had a newsletter migration that was later reverted by the user.
Create a minimal, no-op migration so Django's migration loader can continue.
"""
from django.db import migrations


class Migration(migrations.Migration):
	dependencies = [
		('core', '0002_homepage'),
	]

	operations = [
	]
