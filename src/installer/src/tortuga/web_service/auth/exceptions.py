import cherrypy


class TortugaHTTPAuthError(cherrypy.HTTPError):
    @staticmethod
    def set_response():
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        cherrypy.response.status = 401
        cherrypy.response.body = b'Authentication required'
