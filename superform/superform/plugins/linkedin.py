import json

from flask import redirect, url_for, request, Blueprint
from linkedin import linkedin
from superform.suputils import selenium_utils
from datetime import datetime, timedelta
from superform.suputils import plugin_utils

from superform.models import db, Channel, Publishing

linkedin_verify_callback_page = Blueprint('linkedin', 'channels')

FIELDS_UNAVAILABLE = []
CONFIG_FIELDS = ["channel_name", "linkedin_access_token", "linkedin_token_expiration_date"]
AUTH_FIELDS = True
POST_FORM_VALIDATIONS = {
    'title_max_length': 200,
    'description_max_length': 256,
    'image_type': 'url'
}


def authenticate(channel_id, publishing_id):

    previous_token = LinkedinTokens.get_token(LinkedinTokens, channel_id)

    channel_name = Channel.query.get(channel_id)

    if previous_token.__getitem__(0) is None or (datetime.now() > previous_token.__getitem__(1)) :
        conf = dict()
        conf["channel_name"] = channel_name
        conf["publishing_id"] = publishing_id

    else:
        return 'AlreadyAuthenticated'


def set_access_token(channel_id, code):

    #Add
    channel = Channel.query.get(channel_id)
    channel_name = channel.name
    # add the configuration to the channel
    conf = json.loads(channel.config)
    conf["channel_name"] = channel_name
    conf["linkedin_token_expiration_date"] = (datetime.now() + timedelta(seconds=result.expires_in)).__str__()
    
    LinkedinTokens.put_token(LinkedinTokens, channel_id, conf)
    return conf


def share_post(channel_id, comment, title, submitted_url,submitted_image_url,visibility_code):

    token = LinkedinTokens.get_token(LinkedinTokens, channel_id).__getitem__(0)
    print('share_post token ', token)
    application = linkedin.LinkedInApplication(token=token)
    print('submitted_url', submitted_url)
    if submitted_url is '':
        submitted_url = None
    if submitted_image_url is '':
        submitted_image_url = None

    application.submit_share(comment=comment, title=title, submitted_url=submitted_url,
                             submitted_image_url=submitted_image_url, description="This is a sharing from Superform",visibility_code=visibility_code)
    return True


def auto_auth(url, channel_id):

    driver = selenium_utils.get_chrome()

    driver.get(url)
    username = driver.find_element_by_name("session_key")
    password = driver.find_element_by_name("session_password")

    driver.find_element_by_name("signin").click()

    if not selenium_utils.wait_redirect(driver, 'linkedin'):
        driver.close()
        return redirect(url_for('keepass.error_channel_keepass', chan_id=channel_id))

    driver.close()
    return redirect(url_for('index'))


def run(publishing, channel_config):
    print("publishing Linkedin", publishing)
    print("channel-conf", type(channel_config), channel_config)
    print("conf run", channel_config, type(channel_config))
    conf = json.loads(channel_config)
    channel_name = conf['channel_name']
    authenticate(publishing.channel_id, (publishing.post_id, publishing.channel_id))

    if share_post(publishing.channel_id, publishing.description, publishing.title, publishing.link_url, publishing.image_url, "anyone"):
        publishing.state = 1
        db.session.commit()


def post_pre_validation(post):
    return plugin_utils.post_pre_validation_plugins(post,200,256)


class LinkedinTokens:

    def get_token(self, channel_id):

        channel = Channel.query.get(channel_id)

        if channel and channel.config:
            print("put token", channel.config)
            conf = json.loads(channel.config)
            date_string = conf.get("linkedin_token_expiration_date")

            if date_string == "None" or date_string is None:
                return (None, None)

            date_expiration = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
            print("date_expiration", conf.get("linkedin_access_token"), date_expiration)
            return (conf.get("linkedin_access_token"), date_expiration)

        return (None, None)

    def put_token(self, channel_id, config_json):
        c = Channel.query.get(channel_id)
        c.config = json.dumps(config_json)
        print("put token", config_json)
        db.session.commit()

@linkedin_verify_callback_page.route("/linkedin/verify", methods=['GET'])
def linkedin_verify_authorization():
    code = request.args.get('code')
    conf_publishing = json.loads(request.args.get('state'))
    channel_name = conf_publishing['channel_name']
    publishing_id = conf_publishing['publishing_id']
    post_id = publishing_id.__getitem__(0)
    channel_id = publishing_id.__getitem__(1)
    print("code", code)
    print("post id, channel id", post_id, channel_id)
    channel_config = {}
    if code:
        channel_config = set_access_token(channel_id,code)
    print("channel_config", channel_config)
    #normally should redirect to the channel page or to the page that publish a post
    publishing = Publishing.query.filter_by(post_id=post_id, channel_id=channel_id).first()
    print("init publishing", publishing)
    run(publishing, json.dumps(channel_config))
    return redirect(url_for('index'))
