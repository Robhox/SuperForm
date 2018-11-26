import importlib
import pkgutil
import superform
import os
import pytest

from superform.suputils import keepass, plugin_utils
from flask import Flask
from superform.models import Channel
from superform.models import db as _db
from superform.posts import pre_validate_post
from superform.models import Post


API_KEY = keepass.get_password_from_keepass('linkedin_key')
API_SECRET = keepass.get_password_from_keepass('linkedin_secret')
RETURN_URL = 'http://localhost:5000'

TESTDB = 'test_superform.db'
TESTDB_PATH = "/{}".format(TESTDB)
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI
    app.config['TESTING'] = True
    app.config["PLUGINS"] = {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in pkgutil.iter_modules(superform.plugins.__path__, superform.plugins.__name__ + ".")
    }
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    def teardown():
        _db.drop_all()
        os.unlink(TESTDB_PATH)

    _db.init_app(app)
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session

def test_pre_validate_post_title():
    chan = Channel
    chan.module = "superform.plugins.linkedin"
    pre_validate_post_title(chan,200)

def test_pre_validate_post_description():
    chan = Channel
    chan.module = "superform.plugins.linkedin"
    pre_validate_post_description(chan,256)

def test_prevalidate_post_link_url():
    chan = Channel
    chan.module = "superform.plugins.linkedin"
    pre_validate_post_Link_url(chan)

def test_prevalidate_post_img_url():
    chan = Channel
    chan.module = "superform.plugins.linkedin"
    pre_validate_post_img_url(chan)


def pre_validate_post_title(channel,maxLengthTitle):

    post = Post
    post.title = "x" * maxLengthTitle
    post.description = "x"
    post.link_url = "https://www.test.com"
    post.image_url ="https://www.test.com"
    assert pre_validate_post(channel, post) == 1
    post.title += "x"
    assert  pre_validate_post(channel,post) == 0
    post.title = ""
    assert  pre_validate_post(channel,post) == 0


def pre_validate_post_description(channel, maxLengthDescription):
    post = Post
    post.title = "x"
    post.description = "x" * maxLengthDescription
    post.link_url = "https://www.test.com"
    post.image_url = "https://www.test.com"
    assert  pre_validate_post(channel,post) == 1
    post.description += "x"
    assert  pre_validate_post(channel,post) == 0
    post.description = ""
    assert  pre_validate_post(channel,post) == 0

def pre_validate_post_Link_url(channel):
    post = Post
    post.title = "x"
    post.description = "x"
    post.link_url = "https://www.test.com"
    post.image_url = "https://www.test.com"
    assert  pre_validate_post(channel,post) == 1
    post.link_url = "test error link"
    assert  pre_validate_post(channel,post) == 0
    post.link_url = ""
    assert pre_validate_post(channel,post) == 1

def pre_validate_post_img_url(channel):
    post = Post
    post.title = "x"
    post.description = "x"
    post.link_url = "https://www.test.com"
    post.image_url = "https://www.test.com"
    assert  pre_validate_post(channel,post) == 1
    post.image_url = "test error link"
    assert  pre_validate_post(channel,post) == 0
    post.image_url = ""
    assert pre_validate_post(channel,post) == 1

