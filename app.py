from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS, cross_origin
from os import environ
from datetime import datetime

app = Flask(__name__)
CORS(app)

if environ.get("DEBUG"):
    app.debug = environ.get("DEBUG")
else:
    app.debug = False

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///file.db"
db = SQLAlchemy(app)


class Board(db.Model):
    name = db.Column(db.String(120), unique=True)
    shortcut = db.Column(db.String(3), primary_key=True)

    def __init__(self, name, shortcut):
        self.name = name
        self.shortcut = shortcut

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    created = db.Column(db.DateTime)
    board_id = db.Column(db.String(3), db.ForeignKey('board.shortcut'))
    board = db.relationship('Board',
                            backref=db.backref('posts', lazy='dynamic'))

    parent_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent = db.relation('Post', remote_side='Post.id', backref='replies')

    def __init__(self, text, created, board_id, parent_id):
        self.text = text
        self.created = created
        self.board_id = board_id
        self.parent_id = parent_id

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@app.route("/boards", methods=["GET"])
def boards():
    return jsonify([
        board.as_dict() for board in Board.query.all()])


@app.route("/board/<name>/", methods=["GET"])
def getBoard(name):
    board = db.session.query(Board).get(name)
    response = "Board Not Found", 404
    if board:
        board_dict = board.as_dict()
        board_posts = board.posts
        board_dict["posts"] = [post.as_dict() for post in board_posts]
        response = jsonify(board_dict)

    return response


@app.route("/board/<boardshortcut>/post/<postid>", methods=["GET"])
def viewpost(boardshortcut, postid):
    # Right now we don't NEED the boardshortcut in the url, but we will
    # as we shard the boards
    post = db.session.query(Post).get(postid)
    response = "Post Not Found", 404
    if post:
        post_dict = post.as_dict()
        replies = post.replies
        post_dict["replies"] = [reply.as_dict() for reply in replies]
        response = jsonify(post_dict)

    return response


@app.route("/board", methods=["POST"])
def createBoard():
    board_response = request.get_json()
    newboard = Board(board_response["name"], board_response["shortcut"])
    db.session.add(newboard)
    db.session.commit()
    return jsonify(newboard.as_dict())


@app.route("/board/<boardshortcut>/post", methods=["POST"])
def createPost(boardshortcut):
    post_response = request.get_json()
    parent_id = None

    if("parent_id" in post_response):
        parent_id = post_response["parent_id"]

    newpost = Post(post_response["text"],
                   datetime.now(),
                   boardshortcut,
                   parent_id)

    db.session.add(newpost)
    db.session.commit()
    return jsonify(newpost.as_dict())


if __name__ == "__main__":
    app.run()
