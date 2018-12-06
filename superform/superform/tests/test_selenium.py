import datetime
import pytest

from superform.suputils import selenium_utils
from superform.suputils import keepass
from superform.models import db, Publishing, Post, Authorization, Channel



@pytest.fixture(scope='session', autouse=True)
def prepare():
    #db.execute(db.session.query(Publishing).delete())
    #db.execute(db.session.query(Post).delete())
    #db.execute(db.session.query(Authorization).delete())
    #db.execute(db.session.query(Channel).delete())
    pytest.driver = selenium_utils.get_chrome()
    pytest.now = datetime.datetime.now().strftime("%d%m%Y")

    pytest.linkedin_title_max = 200
    pytest.linkedin_description_max = 256
    pytest.slack_title_max = 40000
    pytest.slack_description_max = 40000

    keepass.set_entry_from_keepass('account_superform')
    selenium_utils.login(pytest.driver, keepass.KeepassEntry.username, keepass.KeepassEntry.password)

    # keepass.set_entry_from_keepass('account_linkedin')
    #selenium_utils.create_channel(pytest.driver, 'test_linkedin', keepass.KeepassEntry.username, keepass.KeepassEntry.password, 'linkedin')
    #
    # keepass.set_entry_from_keepass('account_slack')
    # selenium_utils.create_channel(pytest.driver, 'test_slack', keepass.KeepassEntry.username, keepass.KeepassEntry.password, 'slack')
    # selenium_utils.modify_config(pytest.driver, 2, 'testlingi2255team8', 'general')

    #keepass.set_entry_from_keepass('account_rss')
    selenium_utils.create_simple_channel(pytest.driver, 'test_rss', 'rss')
    selenium_utils.add_authorization(pytest.driver, 'test_rss', 'superego', 2)
    selenium_utils.create_simple_channel(pytest.driver, 'test_gcal', 'gcal')
    selenium_utils.add_authorization(pytest.driver, 'test_gcal', 'superego', 2)
    selenium_utils.modify_config_gcal(pytest.driver, 2,'{"access_token": "ya29.GlxFBgl-MEOI2NojpWSffhjjcfLPhIT55MNauXbQGD4JZQttj45NUKTtaGEd6GpA1GqRUAAhcDYNnK6s7Dyxpx_50N0EPGiKZJrUcPujhrx2eFaRHO94nGrVDpOlVg", "client_id": "408596117278-fkeuv3g0rdkrdpqsch2i1u18h0lgsakm.apps.googleusercontent.com", "client_secret": "EEZoDYXiIq3q-6zoSUrl9ec8", "refresh_token": "1/OEYHMvVkUmfS9C_CVqYccME6zKCANhB_YcU3SwzA2I3VjsBTr4ecnN1CqSchdDXs", "token_expiry": "2018-10-29T17:15:53Z", "token_uri": "https://www.googleapis.com/oauth2/v3/token", "user_agent": None, "revoke_uri": "https://oauth2.googleapis.com/revoke", "id_token": None, "id_token_jwt": None, "token_response": {"access_token": "ya29.GlxFBgl-MEOI2NojpWSffhjjcfLPhIT55MNauXbQGD4JZQttj45NUKTtaGEd6GpA1GqRUAAhcDYNnK6s7Dyxpx_50N0EPGiKZJrUcPujhrx2eFaRHO94nGrVDpOlVg", "expires_in": 3600, "scope": "https://www.googleapis.com/auth/calendar", "token_type": "Bearer"}, "scopes": ["https://www.googleapis.com/auth/calendar"], "token_info_uri": "https://oauth2.googleapis.com/tokeninfo", "invalid": False, "_class": "OAuth2Credentials", "_module": "oauth2client.client"}')
    #selenium_utils.add_authorization(pytest.driver, 'test_linkedin', 'superego', 2)
    #selenium_utils.add_authorization(pytest.driver, 'test_slack', 'superego', 2)

    yield

    pytest.driver.close()

def test_add_post_rss_1():
    title = 'test_rss title 1'
    description = 'test_rss description 1'
    selenium_utils.add_new_post(pytest.driver, ['test_rss'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/2/1"]')

def test_publish_post_rss_1():
    selenium_utils.moderate_post(pytest.driver, 1, 2)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/2/1"]')
    assert "Internal Server Error" not in pytest.driver.title

def test_delete_post_rss_1():
    selenium_utils.delete_post(pytest.driver, 2)
    assert not pytest.driver.find_elements_by_css_selector('a[href="/delete/2"]')

def test_add_post_rss_2():
    title = 'test_rss title 2'
    description = 'test_rss description 2'
    selenium_utils.add_new_post(pytest.driver, ['test_rss'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/3/1"]')

def test_publish_post_rss_2():
    selenium_utils.moderate_post(pytest.driver, 1, 3)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/3/1"]')
    assert "Internal Server Error" not in pytest.driver.title

def test_add_post_rss_empty_begining_date():
    title = 'test_rss title'
    description = 'test_rss description'
    selenium_utils.add_new_post(pytest.driver, ['test_rss'], title, description, '', pytest.now)

    assert "Internal Server Error" in pytest.driver.title


def test_add_post_rss_empty_ending_date():
    title = 'test_rss title'
    description = 'test_rss description'
    selenium_utils.add_new_post(pytest.driver, ['test_rss'], title, description, pytest.now, '')

    assert "Internal Server Error" in pytest.driver.title

def test_add_post_gcal_1():
    title = 'test_gcal title 1'
    description = 'test_gcal description 1'
    selenium_utils.add_new_post(pytest.driver, ['test_gcal'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/4/2"]')
def test_publish_post_gcal_1():
    selenium_utils.moderate_post(pytest.driver, 2, 4)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/4/2"]')
    assert "Internal Server Error" not in pytest.driver.title
def test_add_post_gcal_2():
    title = 'test_gcal title 2'
    description = 'test_gcal description 2'
    selenium_utils.add_new_post(pytest.driver, ['test_gcal'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/5/2"]')

def test_publish_post_gcal_2():
    selenium_utils.moderate_post(pytest.driver, 2, 5)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/5/2"]')
    assert "Internal Server Error" not in pytest.driver.title

def test_add_post_gcal_empty_begining_date():
    title = 'test_gcal title'
    description = 'test_gcal description'
    selenium_utils.add_new_post(pytest.driver, ['test_gcal'], title, description, '', pytest.now)

    assert "Internal Server Error" in pytest.driver.title


def test_add_post_gcal_empty_ending_date():
    title = 'test_gcal title'
    description = 'test_gcal description'
    selenium_utils.add_new_post(pytest.driver, ['test_gcal'], title, description, pytest.now, '')

    assert "Internal Server Error" in pytest.driver.title



"""
def test_add_post_linkedin_1():
    title = 'test_linkedin title 1'
    description = 'test_linkedin description 1'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/1/1"]')


def test_add_post_slack_1():
    title = 'test_slack title 1'
    description = 'test_slack description 1'
    selenium_utils.add_new_post(pytest.driver, ['test_slack'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/2/2"]')


def test_publish_post_linkedin_1():
    selenium_utils.moderate_post(pytest.driver, 1, 1)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/1/1"]')


def test_publish_post_slack_1():
    selenium_utils.moderate_post(pytest.driver, 2, 2)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/2/2"]')


def test_add_post_linkedin_2():
    title = 'test_linkedin title 2'
    description = 'test_linkedin description 2'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/3/1"]')


def test_add_post_slack_2():
    title = 'test_slack title 2'
    description = 'test_slack description 2'
    selenium_utils.add_new_post(pytest.driver, ['test_slack'], title, description, pytest.now, pytest.now, 'https://www.google.be/')

    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/4/2"]')


def test_publish_post_linkedin_2():
    selenium_utils.moderate_post(pytest.driver, 1, 3)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/3/1"]')


def test_publish_post_slack_2():
    selenium_utils.moderate_post(pytest.driver, 2, 4)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/4/2"]')


def test_add_post_linkedin_empty_title():
    title = ''
    description = 'test_slack description'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, pytest.now)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_title"]')


def test_add_post_slack_empty_title():
    title = ''
    description = 'test_linkedin description'
    selenium_utils.add_new_post(pytest.driver, ['test_slack'], title, description, pytest.now, pytest.now)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_title"]')


def test_add_post_linkedin_empty_description():
    title = 'test_linkedin title'
    description = ''
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, pytest.now)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_desc"]')


def test_add_post_slack_empty_description():
    title = 'test_slack title'
    description = ''
    selenium_utils.add_new_post(pytest.driver, ['test_slack'], title, description, pytest.now, pytest.now)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_desc"]')


def test_add_post_linkedin_wrong_title():
    title = "x" * (pytest.linkedin_title_max + 1)
    description = 'test_slack description'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, pytest.now)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_title"]')


def test_add_post_linkedin_wrong_description():
    title = 'test_linkedin title'
    description = "x" * (pytest.linkedin_description_max + 1)
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, pytest.now)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_desc"]')


def test_add_post_linkedin_wrong_link():
    title = 'test_linkedin title'
    description = 'test_linkedin description'
    link = 'test'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, pytest.now, link=link)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_linkUrlPost"]')


def test_add_post_slack_wrong_link():
    title = 'test_linkedin title'
    description = 'test_linkedin description'
    link = 'test'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, pytest.now, link=link)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_linkUrlPost"]')


def test_add_post_linkedin_empty_begining_date():
    title = 'test_linkedin title'
    description = 'test_linkedin description'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, '', pytest.now)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_datefrompost"]')


def test_add_post_linkedin_empty_ending_date():
    title = 'test_linkedin title'
    description = 'test_linkedin description'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, '')

    assert pytest.driver.find_elements_by_css_selector('div[id="error_dateuntilpost"]')


def test_add_post_linkedin_wrong_ending_date():
    title = 'test_linkedin title'
    description = 'test_linkedin description'
    end_date = datetime.datetime.now() - datetime.timedelta(days=1)
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, end_date.strftime("%d%m%Y"))

    assert pytest.driver.find_elements_by_css_selector('div[id="error_dateuntilpost"]')


def test_add_post_slack_empty_begining_date():
    title = 'test_slack title'
    description = 'test_slack description'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, '', pytest.now)

    assert pytest.driver.find_elements_by_css_selector('div[id="error_datefrompost"]')


def test_add_post_slack_empty_ending_date():
    title = 'test_slack title'
    description = 'test_slack description'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, '')

    assert pytest.driver.find_elements_by_css_selector('div[id="error_dateuntilpost"]')


def test_add_post_slack_wrong_ending_date():
    title = 'test_slack title'
    description = 'test_slack description'
    end_date = datetime.datetime.now() - datetime.timedelta(days=1)
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, end_date.strftime("%d%m%Y"))

    assert pytest.driver.find_elements_by_css_selector('div[id="error_dateuntilpost"]')
"""