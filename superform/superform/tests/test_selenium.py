import datetime
import pytest

from superform.suputils import selenium_utils
from superform.suputils import keepass


@pytest.fixture(scope='session', autouse=True)
def prepare():
    pytest.driver = selenium_utils.get_chrome()
    pytest.now = datetime.datetime.now().strftime("%d%m%Y")

    pytest.linkedin_title_max = 200
    pytest.linkedin_description_max = 256
    pytest.slack_title_max = 40000
    pytest.slack_description_max = 40000

    keepass.set_entry_from_keepass('account_superform')
    selenium_utils.login(pytest.driver, keepass.KeepassEntry.username, keepass.KeepassEntry.password)

    keepass.set_entry_from_keepass('account_linkedin')
    selenium_utils.create_channel(pytest.driver, 'test_linkedin', keepass.KeepassEntry.username, keepass.KeepassEntry.password, 'linkedin')

    keepass.set_entry_from_keepass('account_slack')
    selenium_utils.create_channel(pytest.driver, 'test_slack', keepass.KeepassEntry.username, keepass.KeepassEntry.password, 'slack')
    selenium_utils.modify_config(pytest.driver, 2, 'testlingi2255team8', 'general')

    selenium_utils.add_authorization(pytest.driver, 'test_linkedin', 'superego', 2)
    selenium_utils.add_authorization(pytest.driver, 'test_slack', 'superego', 2)

    yield

    pytest.driver.close()


def test_add_post_linkedin():
    title = 'test_linkedin title'
    description = 'test_linkedin description'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/1/1"]')


def test_add_post_slack():
    title = 'test_slack title'
    description = 'test_slack description'
    selenium_utils.add_new_post(pytest.driver, ['test_slack'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/2/2"]')


def test_publish_post_linkedin_1():
    selenium_utils.moderate_post(pytest.driver, 1, 1)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/1/1"]')


def test_publish_post_slack_1():
    selenium_utils.moderate_post(pytest.driver, 2, 2)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/2/2"]')


def test_add_post_linkedin_slack():
    title = 'test_linkedin_slack title'
    description = 'test_linkedin_slack description'
    selenium_utils.add_new_post(pytest.driver, ['test_linkedin', 'test_slack'], title, description, pytest.now, pytest.now, 'https://www.google.be/')
    pytest.driver.get(selenium_utils.index_url)

    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/3/1"]')
    assert pytest.driver.find_elements_by_css_selector('a[href="/moderate/3/2"]')


def test_publish_post_linkedin_2():
    selenium_utils.moderate_post(pytest.driver, 1, 3)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/3/1"]')


def test_publish_post_slack_2():
    selenium_utils.moderate_post(pytest.driver, 2, 3)

    assert not pytest.driver.find_elements_by_css_selector('a[href="/moderate/3/2"]')


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
