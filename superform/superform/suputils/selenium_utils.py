import os
import platform
import sys
import time

from selenium import webdriver, common
from time import sleep


def get_headless_chrome():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    try:
        print(sys.path[0])
        if platform.system() == 'Windows':
            return webdriver.Chrome(sys.path[0] + '\superform\selenium_drivers\chromedriver.exe',
                                    chrome_options=options)
        else:
            return webdriver.Chrome(sys.path[0] + '/superform/selenium_drivers/chromedriver', chrome_options=options)
    except common.exceptions.WebDriverException:
        print(
            'Can not find a valid selenium_drivers driver. it should be named chromedriver on linux or chromedriver.exe '
            'on windows and it should be located in the superform/selenium_drivers folder see this page for '
            'download : https://sites.google.com/a/chromium.org/chromedriver/downloads')


def get_chrome():
    try:
        if platform.system() == 'Windows':
            return webdriver.Chrome(sys.path[0] + '\superform\selenium_drivers\chromedriver.exe')
        else:
            return webdriver.Chrome(sys.path[0] + '/superform/selenium_drivers/chromedriver')
    except common.exceptions.WebDriverException as e:
        print(e)
        print(
            'Can not find a valid selenium_drivers driver. it should be named chromedriver on linux or chromedriver.exe '
            'on windows and it should be located in the superform/selenium_drivers folder see this page for '
            'download : https://sites.google.com/a/chromium.org/chromedriver/downloads')


channel_url = 'http://localhost:5000/channels'
login_url = 'http://localhost:5000/login'
logout_url = 'http://localhost:5000/logout'
authorization_url = 'http://localhost:5000/authorizations'
new_post_url = 'http://localhost:5000/new'
index_url = 'http://localhost:5000'
configure_url = 'http://localhost:5000/configure/'
moderate_url = 'http://localhost:5000/moderate/'
linkedin_url = 'https://www.linkedin.com/'


#---------- Autolog methods
def wait_redirect(driver, url):
    cpt = 0
    while url in driver.current_url:
        time.sleep(.50)
        cpt += 1
        if cpt == 15:
            return False
    return True


def wait_redirect_after(driver, url):
    cpt = 0
    while url not in driver.current_url:
        time.sleep(.50)
        cpt += 1
        if cpt == 10:
            return False
    return True


#---------- Test methods
def login(driver, username, password):
    driver.get(login_url)
    input_username = driver.find_element_by_name("j_username")
    input_password = driver.find_element_by_name("j_password")
    input_username.send_keys(username)
    input_password.send_keys(password)
    driver.find_element_by_css_selector('input[type="submit"]').click()


def create_channel(driver, name, username, password, module):
    driver.get(channel_url)
    driver.find_element_by_css_selector('select[name="module"] option[value="' + module + '"]').click()
    input_name = driver.find_element_by_name("name")
    input_username = driver.find_element_by_name("username")
    input_password = driver.find_element_by_name("password")
    input_name.send_keys(name)
    input_username.send_keys(username)
    input_password.send_keys(password)

    driver.find_element_by_name("add_chan").click()


def modify_config(driver, chan_number, domain_name, channel_name):
    driver.get(configure_url + str(chan_number))
    input_domain_name = driver.find_element_by_name("slack_domain_name")
    input_channel_name = driver.find_element_by_name("slack_channel_name")
    input_domain_name.clear()
    input_channel_name.clear()
    input_domain_name.send_keys(domain_name)
    input_channel_name.send_keys(channel_name)
    driver.find_element_by_css_selector('button[type="submit"]').click()


def add_authorization(driver, name, username, permission):
    driver.get(authorization_url)

    module = driver.find_elements_by_css_selector('button[name="' + name + '"]')
    module[-1].click()
    sleep(1)
    name_id = driver.find_element_by_css_selector('div[class="collapse show"] input[type="hidden"').get_attribute('value')
    input_username = driver.find_element_by_name('username' + name_id)

    input_username.send_keys(username)
    if permission == 2:
        select = driver.find_element_by_css_selector('select[name="permission' + name_id + '"]')
        select.click()
        select.send_keys(u'\ue015')
        select.send_keys(u'\ue007')

    driver.find_element_by_css_selector('a[data-channelid="' + name_id + '"]').click()
    driver.find_element_by_css_selector('button[id="update"]').click()


def add_new_post(driver, name_array, title, description, date_from, date_to, link=''):
    driver.get(new_post_url)

    input_title = driver.find_element_by_name("titlepost")
    input_description = driver.find_element_by_name("descriptionpost")
    input_link = driver.find_element_by_name("linkurlpost")
    input_date_from = driver.find_element_by_name("datefrompost")
    input_date_to = driver.find_element_by_name("dateuntilpost")

    input_title.send_keys(title)
    input_description.send_keys(description)
    input_link.send_keys(link)
    input_date_from.send_keys(date_from)
    input_date_to.send_keys(date_to)

    for name in name_array:
        driver.find_element_by_css_selector('input[data-namechan = "' + name + '"]').click()

    driver.find_element_by_css_selector('button[id="publish-button"]').click()


def moderate_post(driver, chan_number, post_number):
    driver.get(moderate_url + str(post_number) + '/' + str(chan_number))
    driver.find_element_by_css_selector('button[id="publish"]').click()
