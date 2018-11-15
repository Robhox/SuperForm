from flask import Blueprint, url_for, request, redirect, session, render_template, flash

from superform.users import channels_available_for_user
from superform.utils import login_required, datetime_converter, str_converter, get_instance_from_module_path
from superform.models import db, Post, Publishing, Channel, PubGCal

from importlib import import_module
from datetime import date, timedelta

edit_page = Blueprint('edit', __name__)

@edit_page.route('/edit/<int:post_id>', methods=['GET'])
@login_required()
def edit_post(post_id):

    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1

    if user_id == -1:
        return redirect(url_for('index'))

    post = db.session.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()

    if post is None:
        return redirect(url_for('index'))

    channels = channels_available_for_user(user_id)
    publishing = db.session.query(Publishing).filter(Publishing.post_id == post.id).all()

    for i in range(len(publishing)):
        j = 0
        exists = False
        while j < len(channels) and not exists:
            if channels[j].id == publishing[i].channel_id:
                setattr(channels[j], "new", False)
                exists = True
            j = j + 1
        if not exists:
            channel = db.session.query(Channel).get(publishing[i].channel_id)
            instance = get_instance_from_module_path(channel.module)
            unavailable_fields = ','.join(instance.FIELDS_UNAVAILABLE)
            setattr(channel, "unavailablefields", unavailable_fields)
            setattr(channel, "new", True)
            channels.append(channel)

    for channel in channels:
        instance = get_instance_from_module_path(channel.module)
        unavailable_fields = ','.join(instance.FIELDS_UNAVAILABLE)
        setattr(channel, "unavailablefields", unavailable_fields)
        if not hasattr(channel, "new"):
            setattr(channel, "new", True)

    return render_template('edit.html', post=post, publishing=publishing, l_chan=channels)


def publish_edit_post():
    print()
