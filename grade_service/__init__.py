from flask import Flask, request, make_response, abort
import json
import csv
import datetime
import os
from io import StringIO
from sqlite3 import IntegrityError
from .db import get_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'grade_service.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    @app.route('/')
    def hello_world():
        return "Hello World"

    def check_req_field(field, fieldname):
        if field is None:
            abort(400, "Request is missing required field '{}'".format(fieldname))

    @app.route('/grade', methods=['POST'])
    def submit_grade():

        data = request.data
        db = get_db()

        if data:
            json_data = json.loads(data)

            student = json_data.get("student")
            check_req_field(student, "student")

            course = json_data.get("course")
            check_req_field(course, "course")

            course_session = json_data.get("course_session")
            check_req_field(course_session, "course_session")

            assignment = json_data.get("assignment")
            check_req_field(assignment, "assignment")

            points_possible = json_data.get("points_possible")
            check_req_field(points_possible, "points_possible")

            points_scored = json_data.get("points_scored")
            check_req_field(points_scored, "points_scored")

            updated = datetime.datetime.utcnow()

            sql = '''INSERT OR REPLACE INTO assignment_score (
            student,
            course,
            course_session, 
            assignment, 
            points_possible, 
            points_scored,
            updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            '''

            try:
                db.execute(sql, (student, course, course_session, assignment, points_possible, points_scored, updated))
                db.commit()
            except IntegrityError:
                abort(500, "Error saving assignment grade")

        return "created"

    @app.route('/grades/<string:course>/<string:course_session>/<string:assignment>', methods=['GET'])
    def get_grades(course, course_session, assignment):

        db = get_db()
        sql = "SELECT * FROM assignment_score WHERE assignment = ? AND course = ? AND course_session = ?;"
        results = db.execute(sql, (assignment, course, course_session))

        csv_list = [["student", "course", "course_session", "assignment", "points_possible", "points_scored", "created", "updated"]]
        csv_list.extend(results)

        # if csv_list only has 1 row, then query returned 0 results and a 404 should be returned to the client
        if len(csv_list) == 1:
            abort(404)

        filename = "{}-{}-{}-grades.csv".format(course, course_session, assignment)

        si = StringIO()
        cw = csv.writer(si)
        cw.writerows(csv_list)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=" + filename
        output.headers["Content-type"] = "text/csv"
        return output

    return app
