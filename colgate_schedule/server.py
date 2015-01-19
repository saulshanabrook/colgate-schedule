import codecs

import flask
import flask_sslify
import markdown

from . import calendar


app = flask.Flask(__name__)
app.debug = True

flask_sslify.SSLify(app, permanent=True)


@app.route("/")
def introduction():
    input_file = codecs.open("README.md", mode="r", encoding="utf-8")
    text = input_file.read()
    return markdown.markdown(text)


@app.route("/<username>/<password>/")
def ics(username, password):
    response = flask.make_response(str(calendar.get_ics_text(username, password)))
    response.headers['Content-Type'] = 'text/calendar'
    response.headers['Content-Disposition'] = 'attachment; filename=courses.ics'
    return response
