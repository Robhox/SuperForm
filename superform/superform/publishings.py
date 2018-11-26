from flask import Blueprint, url_for, request, redirect, session, render_template
from superform.utils import login_required, datetime_converter, str_converter
from superform.models import db, User, Publishing, Channel, PubGCal
from superform.users import get_moderate_channels_for_user

pub_page = Blueprint('publishings', __name__)

@pub_page.route('/moderate', methods=["GET"])
@login_required()
def moderate():
    user = User.query.get(session.get("user_id", "")) if session.get("logged_in", False) else None
    flattened_list_pubs = []
    if user is not None:
        chans = get_moderate_channels_for_user(user)
        pubs_per_chan = (db.session.query(Publishing).filter((Publishing.channel_id == c.id) & (Publishing.state == 0))
                         for c in chans)
        flattened_list_pubs = [y for x in pubs_per_chan for y in x]
    return render_template("moderate.html", publishings=flattened_list_pubs)

@pub_page.route('/moderate/<int:id>/<string:idc>', methods=["GET", "POST"])
@login_required()
def moderate_publishing(id, idc):

    chn = db.session.query(Channel).filter(Channel.id == idc).first()
    if chn.module == 'superform.plugins.gcal':
        pub = db.session.query(PubGCal).filter(PubGCal.post_id == id, PubGCal.channel_id == idc).first()
        pub.date_start = str_converter(pub.date_start)
        pub.date_end = str_converter(pub.date_end)
    else:
        pub = db.session.query(Publishing).filter(Publishing.post_id == id, Publishing.channel_id == idc).first()
        pub.date_from = str_converter(pub.date_from)
        pub.date_until = str_converter(pub.date_until)

    if request.method == "GET":
        return render_template('moderate_post.html', pub=pub, channel=chn)
    else:
        pub.title = request.form.get('titlepost')
        pub.description = request.form.get('descrpost')
        pub.link_url = request.form.get('linkurlpost')
        pub.image_url = request.form.get('imagepost')
        if chn.module == 'superform.plugins.gcal':
            pub.date_start = datetime_converter(request.form.get('datedebut'))
            pub.hour_start = request.form.get('heuredebut')
            pub.date_end = datetime_converter(request.form.get('datefin'))
            pub.hour_end = request.form.get('heurefin')
            pub.location = request.form.get('location')
            pub.color = request.form.get('color')
            pub.visibility = request.form.get('visibility')
            pub.availability = request.form.get('availability')
        else:
            pub.date_from = datetime_converter(request.form.get('datefrompost'))
            pub.date_until = datetime_converter(request.form.get('dateuntilpost'))
        # state is shared & validated
        """pub.state = 1
        db.session.commit()
        """
        # running the plugin here
        c = db.session.query(Channel).filter(Channel.id == pub.channel_id).first()
        plugin_name = c.module
        c_conf = c.config
        from importlib import import_module
        plugin = import_module(plugin_name)

        # every plugin should implement the autheticate method that redirect to the plugin authentication process
        # if it is required or necessary (no token available or expired)!

        url = plugin.authenticate(c.id, (id, idc))
        if url != "AlreadyAuthenticated":
            print("url", url)
            return plugin.auto_auth(url, pub.channel_id)
        print('publishing publishings.py', pub)
        plugin.run(pub, c_conf)

    return redirect(url_for('index'))
