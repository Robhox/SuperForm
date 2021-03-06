from flask import Blueprint, url_for, current_app, request, redirect, session, render_template , flash

from superform.users import channels_available_for_user
from superform.utils import login_required, datetime_converter, str_converter, get_instance_from_module_path, get_modules_names, get_module_full_name
from superform.models import db, Post, Publishing, Channel

from importlib import import_module

posts_page = Blueprint('posts', __name__)


def create_a_post(form):
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    title_post = form.get('titlepost')
    descr_post = form.get('descriptionpost')
    link_post = form.get('linkurlpost')
    image_post = form.get('imagepost')
    date_from = datetime_converter(form.get('datefrompost'))
    date_until = datetime_converter(form.get('dateuntilpost'))
    p = Post(user_id=user_id, title=title_post, description=descr_post, link_url=link_post, image_url=image_post,
             date_from=date_from, date_until=date_until)
    db.session.add(p)
    db.session.commit()
    return p


def create_a_publishing(post, chn, form):
    chan = str(chn.name)
    title_post = form.get(chan + '_titlepost') if (form.get(chan + '_titlepost') is not None) else post.title
    descr_post = form.get(chan + '_descriptionpost') if form.get(
        chan + '_descriptionpost') is not None else post.description
    plugin = import_module(chn.module)
    if "saveExtraFields" in vars(plugin):
        misc_post = plugin.saveExtraFields(chan, form)  # plugin will handle extra fields here

    link_post = form.get(chan + '_linkurlpost') if form.get(chan + '_linkurlpost') is not None else post.link_url
    image_post = form.get(chan + '_imagepost') if form.get(chan + '_imagepost') is not None else post.image_url
    date_from = datetime_converter(form.get(chan + '_datefrompost')) if datetime_converter(
        form.get(chan + '_datefrompost')) is not None else post.date_from
    date_until = datetime_converter(form.get(chan + '_dateuntilpost')) if datetime_converter(
        form.get(chan + '_dateuntilpost')) is not None else post.date_until
    pub = Publishing(post_id=post.id, channel_id=chn.id, state=0, title=title_post, description=descr_post,
                     link_url=link_post, image_url=image_post,
                     date_from=date_from, date_until=date_until,misc=misc_post)

    db.session.add(pub)
    db.session.commit()
    return pub


@posts_page.route('/new', methods=['GET', 'POST'])
@login_required()
def new_post():
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    list_of_channels = channels_available_for_user(user_id)
    extraForms = {}
    for elem in list_of_channels:
        m = elem.module
        plugin = import_module(m)
        extraForms[elem.name] = plugin.get_template_new()
        clas = get_instance_from_module_path(m)
        unaivalable_fields = ','.join(clas.FIELDS_UNAVAILABLE)
        setattr(elem, "unavailablefields", unaivalable_fields)

    if request.method == "GET":

        post_form_validations = dict()

        print(post_form_validations)
        return render_template('new.html', extra_forms=extraForms, l_chan=list_of_channels, post_form_validations=post_form_validations)
    else:
        create_a_post(request.form)
        return redirect(url_for('index'))

@posts_page.route('/publish', methods=['POST'])
@login_required()
def publish_from_new_post():
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


def pre_validate_post(channel,post):
    plugin = import_module(channel.module)
    return plugin.post_pre_validation(post)
