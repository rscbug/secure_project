import sqlite3
from datetime import datetime

import click
from flask import current_app
from flask import g



def dict_factory(cursor, row):
        d = {}  
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = dict_factory

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
