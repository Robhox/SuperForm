import os
import sys
import platform
from flask import has_request_context, Blueprint, render_template
from pykeepass import PyKeePass
from superform.models import Channel

dir_path = os.path.dirname(os.path.realpath(__file__))
keypass_error_callback_page = Blueprint('keepass', 'channels')

try:
    if platform.system() == 'Windows':
        kp = PyKeePass(dir_path + '\Superform.kdbx', keyfile=dir_path + '\\NewKey.key')
    else:
        kp = PyKeePass(dir_path + '/Superform.kdbx', keyfile=dir_path + '/NewKey.key')

except ImportError or FileNotFoundError:
    print('Please create a Keepass database named Superform with a key file named NewKey.key in the subutils folder')


def set_entry_from_data(title, username=None, password=None, url=None, notes=None):
    """
    Set an entry from data to the class KeepassEntry
    :param title: Title of the Keepass entry
    :param username: Username of the Keepass entry
    :param password: Password of the Keepass entry
    :param url: Url of the Keepass entry
    :param notes: notes of the Keepass entry
    :return:
    """
    KeepassEntry.title = title
    KeepassEntry.username = username
    KeepassEntry.password = password
    KeepassEntry.url = url
    KeepassEntry.notes = notes


def add_entry_in_group(group):
    """
    Add an entry in the keepass based on calss KeepassEntry. The entry will be put in the group specified
    The title of the entry must be UNIQUE !!!!!
    :param group: The nale of the group we want to put the entry in
    :return:
    """
    if not kp.find_entries(title=KeepassEntry.title, first=True):
        group_kp = kp.find_groups(name=group, first=True)
        if group_kp is None:
            group_kp = kp.add_group(kp.root_group, group)
        kp.add_entry(group_kp, KeepassEntry.title, KeepassEntry.username, KeepassEntry.password, KeepassEntry.url, KeepassEntry.notes)
        kp.save()


def delete_entry(title):
    """
    Delete an entry based in the title specified
    :param title: The title of the entry we want to delete
    :return:
    """
    entry_kp = kp.find_entries(title=title, first=True)
    if entry_kp is not None:
        kp.delete_entry(entry_kp)
        kp.save()


def modify_entry_in_group(group, title):
    """
    Modify an entry based on the title and the group specified
    :param group: The group in which the entry is located
    :param title: The title of the entry we want to modify
    :return:
    """
    entry_kp = kp.find_entries(title=title, first=True)
    if KeepassEntry.password == '':
        KeepassEntry.password = entry_kp.password
    if KeepassEntry.username == '':
        KeepassEntry.username = entry_kp.username
    delete_entry(title)
    add_entry_in_group(group)


def get_password_from_keepass(title):
    """
    Get the password contained in the entry described by the title in Keepass
    :param title: The title of the entry we want the password from
    :return: The password of the entry described by the title
    """
    entry = kp.find_entries(title=title, first=True)
    if not entry or not entry.password:
        if has_request_context():
            return 0
        else:
            print('Keepass password is not set for ' + title)
    return entry.password


def get_username_from_keepass(title):
    """
    Get the username contained in the entry described by the title in Keepass
    :param title: The title of the entry we want the username from
    :return: The username of the entry described by the title
    """
    entry = kp.find_entries(title=title, first=True)
    if not entry or not entry.username:
        if has_request_context():
            return 0
        else:
            print('Keepass username is not set for ' + title)
    return entry.username


def set_entry_from_keepass(title):
    """
    Set an entry described by title from Keepass to the class KeepassEntry
    :param title: The title of the entry we are looking for
    :return:
    """
    entry = kp.find_entries(title=title, first=True)
    if not entry or not entry.username or not entry.password:
        if has_request_context():
            return 0
        else:
            if entry.username is None and entry.password is None:
                print('Keepass username and password are not set for ' + title)
            elif entry.password is None:
                print('Keepass password is not set for ' + title)
            else:
                print('Keepass username is not set for ' + title)
    KeepassEntry.title = entry.title
    KeepassEntry.username = entry.username
    KeepassEntry.password = entry.password
    print('usr', entry.username)
    print('pwd', entry.password)
    KeepassEntry.url = entry.url
    KeepassEntry.notes = entry.notes


class KeepassEntry:
    title = ''
    username = ''
    password = ''
    url = ''
    notes = ''


@keypass_error_callback_page.route('/error_channel_keepass/<int:chan_id>')
def error_channel_keepass(chan_id):
    chan_name = Channel.query.get(chan_id).name
    return render_template('error_channel_keepass.html', channel=chan_name)
