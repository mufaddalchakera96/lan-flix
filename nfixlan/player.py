from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort

from nfixlan.auth import login_required
from nfixlan.db import get_db

import os
import mimetypes
import datetime

bp = Blueprint('player', __name__)

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    user_id = g.user['id']
    db = get_db()
    history = []
    catalogue = []
    data_path = request.args.get('data_path')
    send_history = False
    if(data_path is None):
        data_path = current_app.config['DATA_PATH']
        send_history = True
    description = None
    logo = None
    
    if(send_history):
        entries = db.execute(
                'SELECT * FROM watch_history WHERE user_id = ? ORDER BY created DESC', (user_id,)
        ).fetchall()
        for row in entries:
            l = [row['title'], True, None, None]
            history.append(l)
    
    # The way this catalogue works is probably bad.. need to add code
    # for bookkeeping these things in a db, and then fetch from the db.
    # This hack works for now. 
    for f in os.listdir(data_path):
        path = ""
        if(data_path[-1] == "\\"):
            path = data_path + f
        else:
            path = data_path + "\\" + f
        
        is_file = os.path.isfile(path)
        
        if(is_file and f == "logo.png"):
            logo = path
        elif(is_file and f == "description.txt"):
            with open(path, "r") as description_f:
                description = description_f.read()
        elif(is_file):
            l = [path, True, None, None]
            catalogue.append(l)
        else:
            d = "No Description"
            if os.path.isfile(path + "\\description.txt"):
                with open(path + "\\description.txt", "r") as description_f:
                    d = description_f.read()
            l = [path, False, (path + "\\logo.png") if os.path.isfile(path + "\\logo.png") else None, d]
            catalogue.append(l)

    #this below is the worst way of doing this one could possibly do,
    #but it was 2AM in the night and I couldn't be bothered with HTML
    #so this is the laziest way I could come up with.
    i = 0
    data = []
    while(i < len(history) or i < len(catalogue)):
        l = [None, None]
        if(i < len(catalogue)):
            l[0] = catalogue[i]
        if(i < len(history)):
            l[1] = history[i]
        data.append(l)
        i += 1
    return render_template('player/index.html', path = data_path, data = data, description = description, logo = logo)
    
    
@bp.route('/play', methods=('GET', 'POST'))
@login_required
def play():
    src = request.args.get('src')
    if src is None:
        return redirect(url_for(player.index))
    user_id = g.user['id']
    title = src.split("\\")[-1]
    time = 0
    history_id = -1
    db = get_db()
    entry = db.execute(
            'SELECT * FROM watch_history WHERE user_id = ? and title=?', (user_id,src,)
    ).fetchone()
    if entry != None:
        time = entry['seek_position']
        history_id = entry['id']
    else:
        #insert new row
        db.execute(
            'INSERT INTO watch_history (user_id, created, title, seek_position) VALUES (?, ?, ?, ?)',
            (user_id, datetime.datetime.now(), src, time)
        )
        db.commit()
        entry = db.execute(
            'SELECT * FROM watch_history WHERE user_id = ? and title=?', (user_id,src,)
        ).fetchone()
        history_id = entry['id']
    return render_template('player/player.html', src = src, title = title, mime= mimetypes.guess_type(src)[0], time=time, history_id = history_id)
    
@bp.route('/update_history', methods=('GET', 'POST'))
@login_required
def update_history():
    if request.method == "POST":
        time = request.form['time']
        history_id = request.form['history_id']
        db = get_db()
        entry = db.execute(
            'SELECT * FROM watch_history WHERE id=?', (history_id,)
        ).fetchone()
        if(entry != None):
            db.execute(
                'UPDATE watch_history SET created = ?, seek_position = ? WHERE id=?',
                (datetime.datetime.now(), time, history_id,)
            )
            db.commit()
        else:
            return "Something is Wrong"
    return "Successful"

@bp.route('/src', methods=('GET', 'POST'))
@login_required
def src():
    src = request.args.get('src')
    directory = "\\".join(src.split("\\")[:-1])
    file = src.split("\\")[-1]
    print(directory, file)
    return send_from_directory(directory,
                               file, as_attachment = True)
