from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
from .utils import encrypt_data, get_hash, decrypt_data

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)

@bp.route("/show")
@login_required
def show():
    """Show all the posts and decrypt body for login user"""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()

    for post in posts:
        if g.user['id'] == post['author_id']:
            post["body"]=decrypt_data(get_hash(g.user['username']), str(g.user['id'])*16, post["body"])
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id."""
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form.get("body", "Null")
        error = None
               
        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()            
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, encrypt_data(get_hash(g.user['username']), str(g.user['id'])*16, body), g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.show"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)
    post["body"]=decrypt_data(get_hash(g.user['username']), str(g.user['id'])*16, post["body"])
       
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None
        
        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, encrypt_data(get_hash(g.user['username']), str(g.user['id'])*16, body), id)
            )
            db.commit()
            return redirect(url_for("blog.show"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post."""
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
