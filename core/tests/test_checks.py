from django.test import TestCase, override_settings
from django.core import checks


class VapidCheckTests(TestCase):
    def test_vapid_missing_reports_error(self):
        with override_settings(VAPID_PUBLIC_KEY=None, VAPID_PRIVATE_KEY=None, VAPID_CLAIMS_SUBJECT=None):
            errors = checks.run_checks()
            # Look for our core.E001 id in the errors
            ids = [e.id for e in errors if hasattr(e, 'id')]
            self.assertIn('core.E001', ids)

    def test_vapid_present_no_errors(self):
        with override_settings(VAPID_PUBLIC_KEY='a', VAPID_PRIVATE_KEY='b', VAPID_CLAIMS_SUBJECT='mailto:me@example.com'):
            errors = checks.run_checks()
            ids = [e.id for e in errors if hasattr(e, 'id')]
            self.assertNotIn('core.E001', ids)
