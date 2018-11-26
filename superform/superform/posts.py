from flask import Blueprint, url_for, current_app, request, redirect, session, render_template, flash

from superform.users import channels_available_for_user
from superform.utils import login_required, datetime_converter, str_converter, get_instance_from_module_path, get_modules_names, get_module_full_name
from superform.models import db, Post, Publishing, Channel, PubGCal

from importlib import import_module
from datetime import date, timedelta

posts_page = Blueprint('posts', __name__)


def create_a_post(form):  # called in publish_from_new_post() & new_post()
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    title_post = form.get('titlepost')
    descr_post = form.get('descriptionpost')
    link_post = form.get('linkurlpost')
    image_post = form.get('imagepost')
    if form.get('datefrompost') is '':
        # set default date if no date was chosen
        date_from = date.today()
    else:
        date_from = datetime_converter(form.get('datefrompost'))
    if form.get('dateuntilpost') is '':
        date_until = date.today() + timedelta(days=7)
    else:
        date_until = datetime_converter(form.get('dateuntilpost'))
    p = Post(user_id=user_id, title=title_post, description=descr_post, link_url=link_post, image_url=image_post,
             date_from=date_from, date_until=date_until)
    db.session.add(p)
    db.session.commit()
    return p


def create_a_publishing(post, chn, form):  # called in publish_from_new_post()

    chan = str(chn.name)
    validate = pre_validate_post(chn, post)
    if validate == -1 or validate == 0:
        return validate

    title_post = form.get(chan + '_titlepost') if (form.get(chan + '_titlepost') is not None) else post.title
    descr_post = form.get(chan + '_descriptionpost') if form.get(
        chan + '_descriptionpost') is not None else post.description
    link_post = form.get(chan + '_linkurlpost') if form.get(chan + '_linkurlpost') is not None else post.link_url
    image_post = form.get(chan + '_imagepost') if form.get(chan + '_imagepost') is not None else post.image_url

    if chn.module == 'superform.plugins.gcal':

        date_start = datetime_converter(form.get(chan + '_datedebut')) if datetime_converter(
            form.get(chan + '_datedebut')) is not None else post.date_from
        date_end = datetime_converter(form.get(chan + '_datefin')) if datetime_converter(
            form.get(chan + '_datefin')) is not None else post.date_until
        hour_start = form.get(chan + '_heuredebut') if form.get(chan + '_heuredebut') is not None else '00:00'
        hour_end = form.get(chan + '_heurefin') if form.get(chan + '_heurefin') is not None else '00:00'
        location = form.get(chan + '_location')
        color_id = form.get(chan + '_color')
        guests = form.get(chan + '_guests')
        visibility = form.get(chan + '_visibility')
        # availability = form.get(chan + '_availability')

        pub = PubGCal(post_id=post.id, channel_id=chn.id, state=0, title=title_post, description=descr_post,
                      link_url=link_post, image_url=image_post,
                      date_from=None, date_until=None, date_start=date_start, date_end=date_end,
                      location=location, color_id=color_id, hour_start=hour_start, hour_end=hour_end,
                      guests=guests, visibility=visibility)  # , availability=availability)
    else:
        if form.get(chan + 'datefrompost') is '':
            date_from = date.today()
        else:
            date_from = datetime_converter(form.get(chan + '_datefrompost')) if datetime_converter(
                form.get(chan + '_datefrompost')) is not None else post.date_from
        if form.get(chan + 'dateuntilpost') is '':
            date_until = date.today() + timedelta(days=7)
        else:
            date_until = datetime_converter(form.get(chan + '_dateuntilpost')) if datetime_converter(
                form.get(chan + '_dateuntilpost')) is not None else post.date_until
    pub = Publishing(post_id=post.id, channel_id=chn.id, state=0, title=title_post, description=descr_post,
                     link_url=link_post, image_url=image_post,
                     date_from=date_from, date_until=date_until)

    db.session.add(pub)
    db.session.commit()
    return pub


@posts_page.route('/new', methods=['GET', 'POST'])
@login_required()
def new_post():
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    list_of_channels = channels_available_for_user(user_id)
    for elem in list_of_channels:
        m = elem.module
        clas = get_instance_from_module_path(m)
        unavailable_fields = ','.join(clas.FIELDS_UNAVAILABLE)
        setattr(elem, "unavailablefields", unavailable_fields)
        setattr(elem, "plugin_name", str(m))

    if request.method == "GET":  # when clicking on the new post tab
        # set default date
        default_date = {'from': date.today(), 'until': date.today() + timedelta(days=7)}
        mods = get_modules_names(current_app.config["PLUGINS"].keys())
        post_form_validations = dict()

        print(post_form_validations)
        return render_template('new.html', l_chan=list_of_channels, post_form_validations=post_form_validations,date=default_date)
    else:
        create_a_post(request.form)
        return redirect(url_for('index'))


@posts_page.route('/publish', methods=['POST'])
@login_required()
def publish_from_new_post():  # when clicking on 'save and publish' button
    # First create the post
    p = create_a_post(request.form)
    # then treat the publish part
    if request.method == "POST":
        error_id  = "";
        state_error = False;
        for elem in request.form:
            if elem.startswith("chan_option_"):
                def substr(elem):
                    import re
                    return re.sub('^chan\_option\_', '', elem)
                c = Channel.query.get(substr(elem))
                validate = pre_validate_post(c, p)
                if validate == 0:
                    state_error = True
                    error_id = str(p.id) + ","
                # for each selected channel options
                # create the publication
                create_a_publishing(p, c, request.form)
        if state_error:
            error_id = error_id[:-1]
            error = "error in post :", error_id, " field(s) not valid"
            flash(error, "danger")
            return redirect(url_for('index'))
    db.session.commit()
    return redirect(url_for('index'))


@posts_page.route('/records')
@login_required()
def records():
    posts = db.session.query(Post).filter(Post.user_id == session.get("user_id", ""))
    records = [(p) for p in posts if p.is_a_record()]
    return render_template('records.html', records=records)


def pre_validate_post(channel, post):
    plugin = import_module(channel.module)
    return plugin.post_pre_validation(post)
