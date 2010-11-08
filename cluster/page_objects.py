# toying with the idea of using PageObjects for testing purposes, but I am not
# sure I am getting it quite yet.  Inspired by this talk a columbus code camp.
# http://www.cheezyworld.com/2010/10/17/slides-from-columbus-code-camp/

class LoginPage(object):
    def __init__(self, client):
        self.url = '/accounts/login/'
        self.client = client

    def visit(self):
        self.response = self.client.get(self.url)

    def login(self, username, password, nexturl=''):
        """
        If nexturl is provided a 302 redirect is issues to that URL after
        a successful login.
        """
        if nexturl == '':
            url = self.url
        else:
            url = self.url + '?next=' + nexturl
        self.response = self.client.post(url, {
            'username': username,
            'password': password,
        })


class DashboardPage(object):
    def __init__(self, client):
        self.url = '/'
        self.client = client

    def launch(self, cluster_id):
        # FIXME: This should be a POST
        response = self.client.get('/cluster/' + cluster_id + '/launch')
        return LaunchPage(self.client, response)

    def get_history(self, cluster_id):
        "Returns the HistoryPage Object"
        response = self.client.get('/cluster/' + cluster_id + '/history')
        return HistoryPage(self.client, response)

    def get_ssh_key(self):
        "Returns a string containing the SSH key"
        response = self.client.get('/cluster/account/ssh_key')
        return response.content


class HistoryPage(object):
    def __init__(self, client, response):
        self.client = client
        self.response = response


class LaunchPage(object):
    def __init__(self, client, response):
        self.client = client
        self.response = response


class RegisterPage(object):
    def __init__(self):
        self.url = '/cluster/register/'
