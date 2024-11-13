from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo', __name__)

@bp.route('/')
@login_required
def index():
    db, c = get_db()
    c.execute(
        'SELECT t.id, description, created_at, completed, created_by, username'
        ' FROM todo t JOIN user u ON t.created_by = u.id where u.id = %s'
        ' ORDER BY created_at DESC', (g.user['id'],)
    )
    todos = c.fetchall()
    return render_template('todo/index.html', todos=todos)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        description = request.form['description']
        error = None

        if not description:
            error = 'Description is required.'

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'INSERT INTO todo (description, completed, created_by) VALUES (%s, %s, %s)',
                (description, False, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html')

def get_todo(id):
    db, c = get_db()
    c.execute(
        'SELECT t.id, description, created_at, completed, created_by, username'
        ' FROM todo t JOIN user u ON t.created_by = u.id'
        ' WHERE t.id = %s',
        (id,)
    )
    todo = c.fetchone()

    if todo is None:
        abort(404, "Todo id {0} doesn't exist.".format(id))

    return todo

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    todo = get_todo(id)

    if request.method == 'POST':
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        error = None

        if not description:
            error = 'Description is required.'

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'UPDATE todo SET description = %s, completed = %s WHERE id = %s and created_by = %s',
                (description, completed, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update.html', todo=todo)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_todo(id)
    db, c = get_db()
    c.execute('DELETE FROM todo WHERE id = %s and created_by = %s', (id, g.user['id']))
    db.commit()
    return redirect(url_for('todo.index'))
