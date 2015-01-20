import os

from livereload import Server, shell
import werkzeug.debug

from . import server

app = werkzeug.debug.DebuggedApplication(server.app, evalex=True)

server = Server(app)
server.watch('colgate_schedule/*.py')
server.serve(port=os.environ['PORT'])
