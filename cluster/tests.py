"""
This is a placeholder.  Doctests should only be used as brief examples inline
in the code.  Otherwise, most testing should be done as lettuce features, see
the cluster/features directory.
"""

from django.test import TestCase
import re


class SimpleTest(TestCase):
    def test_register_present(self):
        response = self.client.get('/cluster/register/')
        self.failUnlessEqual(response.status_code, 200)

    def test_login_present(self):
        response = self.client.get('/accounts/login/')
        self.failUnlessEqual(response.status_code, 200)


class LoginTest(TestCase):
    fixtures = [ 'TestUser.json' ]

    def test_login_failure(self):
        response = self.client.post('/accounts/login/', {
                    'username': 'missinguser',
                    'password': 'none',
                })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search(
                    r"(Username and password didn't match. Please try again.)",
                    response.content
                    ),
                    "A Failed login did not return the right message.")

    def test_login_success(self):
        response = self.client.post('/accounts/login/?next=/', {
                    'username': 'user001',
                    'password': 'wombat',
                })
        self.assertEqual(response.status_code,
                302,
                "User login probably failed."
                )
        self.assertEqual(response['Location'], 'http://testserver/')

class AccessTest(TestCase):
    fixtures = [
            'TestUser.json',
            'TestClusterTemplate.json',
            'Ec2InstanceType.json'
            ]

    # A user should be able to launch his own cluster
    def test_cluster_launch(self):
        response = self.client.post('/accounts/login/?next=/', {
                    'username': 'user001',
                    'password': 'wombat',
                })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/')
        # FIXME: This should be a POST
        response = self.client.get('/cluster/1/launch')
        self.assertEqual(response.status_code, 200)
        match_string = "The following cluster is launching:"
        self.assertTrue(re.search(match_string, response.content))
 
    # A user should be able to access his own cluster history
    def test_cluster_history(self):
        response = self.client.post('/accounts/login/?next=/', {
                    'username': 'user001',
                    'password': 'wombat',
                })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/')
        # FIXME: This should be a POST
        response = self.client.get('/cluster/1/history')
        self.assertEqual(response.status_code, 200)
        match_string = "Cluster History for"
        self.assertTrue(re.search(match_string, response.content))

    # A user should be able to access his own SSH Key
    # A user should be able to access his own Profile
    # A user should be able to edit his own Profile

    # A user should not be able to launch other clusters
    def test_denied_cluster_launch(self):
        response = self.client.post('/accounts/login/?next=/', {
                    'username': 'user001',
                    'password': 'wombat',
                })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/')
        # FIXME: This should be a POST
        response = self.client.get('/cluster/2/launch')
        #print response.content
        self.assertEqual(response.status_code, 200)
        match_string = "Cluster Access Denied"
        self.assertTrue(re.search(match_string, response.content))

    # A user should not be able to access other cluster histories
    # A user should not be able to access other SSH Keys
    # A user should not be able to access other Profiles
    # A user should not be able to edit other Profiles
