"""
This is a placeholder.  Doctests should only be used as brief examples inline in
the code.  Otherwise, most testing should be done as lettuce features, see the
cluster/features directory.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_register(self):
        response = self.client.get('/cluster/register/')
        self.failUnlessEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.get('/accounts/login/')
        self.failUnlessEqual(response.status_code, 200)

