from lettuce import *
from lxml import html
from django.test.client import Client
from nose.tools import assert_equals, assert_true
import logging

LOG_FILENAME = 'test-debug.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

@before.all
def set_browser():
    world.browser = Client()

@step(r'I access the url "(.*)"')
def access_url(step, url):
    response = world.browser.get(url)
    if response.status_code == 200:
        # Only try and generate the DOM if you actually get a valid response
        world.dom = html.fromstring(response.content)
    elif response.status_code == 302:
        world.status_code = response.status_code
        world.location = response['Location']

@step(r'I see the form "(.*)"')
def see_header(step, form_id):
    form = world.dom.cssselect('#' + form_id)
    assert_true(form, "There is no form with id " + form_id)

@step(r'I see the header "(.*)"')
def see_header(step, text):
    header = world.dom.cssselect('h3')[0].text.strip()
    assert_equals(
            header,
            text,
            "Did not find header with content '" + text + "'"
            )

@step(u'Then I am redirected to the url "(.*)"')
def then_i_am_redirected_to_the_url(step, url):
    assert_equals(302, world.status_code, "Did not receive 302 redirect")
    # .find returns -1 when there is no match
    assert_true(world.location.find(url) >= 0, 
        "Was not redirected to the correct location")


