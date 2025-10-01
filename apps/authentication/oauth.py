# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from flask import current_app as app 
from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.contrib.google import google, make_google_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from apps.config import Config
from .models import Users, db
from flask import redirect, url_for
from flask import flash


