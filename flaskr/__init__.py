from flask import Flask, request, jsonify, render_template
from jinja2 import TemplateNotFound
from werkzeug.exceptions import InternalServerError, BadRequest

from database.models import setup_db, TodoItem, db_drop_and_create_all

STATIC_DIRECTORY = "../client/build"


def create_app():

    app = Flask(__name__, static_url_path="", template_folder=STATIC_DIRECTORY, static_folder=STATIC_DIRECTORY)
    setup_db(app)

    # Use this to re-initialize database:
    db_drop_and_create_all()

    @app.errorhandler(404)
    def static_handler(e):
        try:
            render = render_template("index.html")
        except TemplateNotFound as exception:
            return e
        return render, 200

    @app.route("/api/todo", methods=["GET"])
    def get_all_todo():
        todo_list = [todo.dictionary() for todo in TodoItem.query.all()]
        return jsonify(todo_list), 200

    @app.route("/api/todo", methods=["POST"])
    def add_todo():
        description = request.json.get("description", None)
        if not description:
            raise BadRequest("Required body parameter \"description\" not found.")
        todo = TodoItem(description=description, done=False)
        todo.insert()
        return jsonify(todo.dictionary()), 201

    @app.route("/api/todo", methods=["PUT"])
    def update_todo():
        todo_id = request.json.get("id", None)
        if not todo_id:
            raise BadRequest("Required body parameter \"id\" not found.")
        description = request.json.get("description", None)
        done = request.json.get("done", None)
        todo = TodoItem.get(todo_id)
        todo.description = description if description else todo.description
        todo.done = done
        todo.update()
        return jsonify(todo.dictionary()), 200

    @app.route("/api/todo", methods=["DELETE"])
    def delete_todo():
        todo_id = request.args.get("id", None)
        if not todo_id:
            raise BadRequest("Required query parameter \"id\" not found.")
        todo = TodoItem.get(todo_id)
        todo.delete()
        return jsonify({}), 200

    @app.errorhandler(InternalServerError)
    def server_error(error):
        return jsonify(code="SERVER_ERROR", message="An internal server error occurred."), error.code

    @app.errorhandler(BadRequest)
    def bad_request_error(error):
        return jsonify(code="BAD_REQUEST", message=error.description), error.code

    return app
