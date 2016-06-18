from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)

if environ.get("DEBUG"):
    app.debug = environ.get("DEBUG")
else:
    app.debug = False

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///file.db"
db = SQLAlchemy(app)


class Board(db.Model):
    name = db.Column(db.String(120), unique=True)
    shortcut = db.Column(db.String(3), primary_key=True)

    def __init__(self, name, title):
        self.name = name
        self.title = title


@app.route("/boards", methods=["GET"])
def boards():
    return jsonify([
        {"id": "py"},
        {"id": "dj"},
        {"id": "fl"},
        {"id": "sci"},
        {"id": "num"}])


@app.route("/board/<name>", methods=["GET"])
def getBoard():
    return ""


@app.route("/board", methods=["POST"])
def createBoard():
    return ""


@app.route("/board/<name>/post", methods=["POST"])
def createPost():
    return ""

if __name__ == "__main__":
    app.run()
