# -*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function, division

# The Guardian anonymous user is different to the Django Anonymous user. The Django Anonymous user does not have an entry in the database, however the Guardian anonymous user does. This means that the following code will return an unexpected result:
#
# from guardian.compat import get_user_model
# User = get_user_model()
# anon = User.get_anonymous()
# anon.is_anonymous()   # returns False
# If ANONYMOUS_USER_ID is set to None, anonymous user object permissions are disabled. You may need to choose this option if creating a User object to represent anonymous users would be problematic in your environment.
ANONYMOUS_USER_ID = -1

GUARDIAN_RAISE_403 = False
GUARDIAN_RENDER_403 = False
GUARDIAN_TEMPLATE_403 = '403.html'

# Due to changes introduced by Django 1.5 user model can have differently named username field (it can be removed too,
#  but guardian currently depends on it). After syncdb command we create anonymous user for convenience,
# however it might be necessary to set this configuration in order to set proper value at username field.
# ANONYMOUS_DEFAULT_USERNAME_VALUE = None

# Guardian supports object level permissions for anonymous users, however when in our project we use custom User model,
# default function might fail.This can lead to issues as guardian tries to create anonymous user after each syncdb call.
# Object that is going to be created is retrieved using function pointed by this setting.
# Once retrieved, save method would be called on that instance.
GUARDIAN_GET_INIT_ANONYMOUS_USER = 'guardian.management.get_init_anonymous_user'
