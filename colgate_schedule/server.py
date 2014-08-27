import flask

from . import calendar


app = flask.Flask(__name__)
app.debug = True


@app.route("/")
def introduction():
    return flask.render_template('index.html')


@app.route("/<username>/<password>")
def ics(username, password):
    response = flask.make_response(str(calendar.get_ics_text(username, password)))
    response.headers['Content-Type'] = 'text/calendar'
    response.headers['Content-Disposition'] = 'attachment; filename=courses.ics'
    return response
