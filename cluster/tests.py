"""
I would really like to be doing ATDD and working off of lettuce tests instead,
but I don't feel that I have that figured out yet.  I am using this as a crutch
at this point.
"""

from django.test import TestCase
from cluster.page_objects import LoginPage, RegisterPage, DashboardPage
import re


class SimpleTest(TestCase):
    def test_register_present(self):
        page = RegisterPage()
        response = self.client.get(page.url)
        self.failUnlessEqual(response.status_code, 200)

    def test_login_present(self):
        page = LoginPage(self.client)
        page.visit()
        self.failUnlessEqual(page.response.status_code, 200)


class LoginTest(TestCase):
    fixtures = [ 'TestUser.json' ]

    def test_login_failure(self):
        page = LoginPage(self.client)
        page.login('missinguser', 'badpass')
        response = page.response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search(
                    r"(Username and password didn't match. Please try again.)",
                    response.content
                    ),
                    "A Failed login did not return the right message.")

    def test_login_success(self):
        page = LoginPage(self.client)
        page.login('user001', 'wombat', '/')
        response = page.response
        self.assertEqual(response.status_code,
                302,
                "User login probably failed."
                )
        self.assertEqual(response['Location'], 'http://testserver/')

class AccessTest(TestCase):
    fixtures = [
            'TestUser.json',
            'TestClusterTemplate.json',
            'TestAwsCredential.json',
            'Ec2InstanceType.json'
            ]

    def setUp(self):
        page = LoginPage(self.client)
        page.login('user001', 'wombat')

    # A user should be able to launch his own cluster
    def test_cluster_launch(self):
        dashboard_page = DashboardPage(self.client)
        launch_page = dashboard_page.launch('1')
        response = launch_page.response
        self.assertEqual(response.status_code, 200)
        match_string = "The following cluster is launching:"
        self.assertTrue(re.search(match_string, response.content))
 
    # A user should be able to access his own cluster history
    def test_cluster_history(self):
        dashboard_page = DashboardPage(self.client)
        history_page = dashboard_page.goto_history('1')
        response = history_page.response
        self.assertEqual(response.status_code, 200)
        match_string = "Cluster History for"
        self.assertTrue(re.search(match_string, response.content))

    # A user should be able to access his own SSH Key
    def test_get_ssh_key(self):
        dashboard_page = DashboardPage(self.client)
        ssh_key = dashboard_page.get_ssh_key()
        match_string = "BEGIN RSA PRIVATE KEY"
        self.assertTrue(re.search(match_string, ssh_key))

    # A user should be able to access his own Profile
    def test_goto_account(self):
        dashboard_page = DashboardPage(self.client)
        account_page = dashboard_page.goto_account()
        self.assertEqual(account_page.response.status_code, 200)
        match_string = "Account Information for user001"
        self.assertTrue(
                re.search(match_string, account_page.response.content),
                "String not found: " + match_string
                )

    # A user should be able to edit his own Profile

    # A user should not be able to launch other clusters
    def test_cluster_launch_denied(self):
        dashboard_page = DashboardPage(self.client)
        launch_page = dashboard_page.launch('2')
        response = launch_page.response
        self.assertEqual(response.status_code, 200)
        match_string = "Cluster Access Denied"
        self.assertTrue(re.search(match_string, response.content))

    # A user should not be able to access other cluster histories
    def test_cluster_history_denied(self):
        dashboard_page = DashboardPage(self.client)
        history_page = dashboard_page.goto_history('2')
        response = history_page.response
        self.assertEqual(response.status_code, 200)
        match_string = "Cluster History Access Denied"
        self.assertTrue(re.search(match_string, response.content))

    # A user should not be able to edit other Profiles

    # A logged in user should be able to change his password

    # An unauthenticated user should be able to create an account.
