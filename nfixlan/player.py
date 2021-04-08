from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from nfixlan.auth import login_required
from nfixlan.db import get_db

import os

bp = Blueprint('player', __name__)

@bp.route('/')
def index():
    return render_template('player/index.html', posts=[])