# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=no-member

import argparse
import json
import logging.config
import logging.handlers
import os.path
import sys
from pathlib import Path

import cherrypy
from cherrypy.process import plugins

from tortuga.kit.loader import load_kits
from tortuga.logging import KIT_NAMESPACE, ROOT_NAMESPACE, \
    WEBSERVICE_NAMESPACE
from . import controllers, controllers_v2, rootRouteMapper
from .app import app
from .auth import methods as auth_methods
from .auth.authenticator import CherryPyAuthenticator
from .controllers.tortugaController import TortugaController
from .plugins.database import DatabasePlugin
from .plugins.websocket import WebsocketPlugin
from .tools.database import DatabaseTool

# read logging configuration
log_conf_file = Path(app.cm.getEtcDir()) / 'tortugawsd.log.conf'
if log_conf_file.exists():
    logging.config.fileConfig(str(log_conf_file))

# Log everything 'tortuga.*'
root_logger = logging.getLogger(ROOT_NAMESPACE)

# and everything 'tortuga_kits.*'
tortuga_kits_logger = logging.getLogger(KIT_NAMESPACE)

if not log_conf_file.exists():
    # in the absence of a `tortugawsd` logging configuration, use
    # sane defaults
    root_logger.setLevel(logging.DEBUG)
    tortuga_kits_logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.handlers.TimedRotatingFileHandler(
        '/var/log/tortugawsd', when='midnight')
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    root_logger.addHandler(ch)

    tortuga_kits_logger.addHandler(ch)


logger = logging.getLogger(WEBSERVICE_NAMESPACE)


def prepare_server():
    """
    Prepare server.

    """
    logger.debug('Loading service configuration')

    config = {
        '/': {
            'tools.db.on': True,
            'response.headers.server': 'Tortuga web service',
            'request.dispatch': rootRouteMapper.setupRoutes(),
        },
        '/v1': {
            'request.dispatch': controllers.setup_routes()
        },
        '/v2': {
            'request.dispatch': controllers_v2.setup_routes()
        }
    }

    # No root controller as we provided our own.
    return cherrypy.tree.mount(root=None, config=config)


def run_server(daemonize: bool = False, pidfile: str = None,
               debug: bool = False):
    logger.debug('Starting service')

    #
    # Load kits
    #
    load_kits()

    #
    # Initialize plugins
    #
    if daemonize:
        plugins.Daemonizer(cherrypy.engine).subscribe()

    if pidfile:
        plugins.PIDFile(cherrypy.engine, pidfile).subscribe()

    DatabasePlugin(cherrypy.engine).subscribe()

    WebsocketPlugin(
        app.cm.getWebsocketScheme(),
        app.cm.getWebsocketPort(),
        cherrypy.engine,
        debug=debug
    ).subscribe()

    #
    # Setup the signal handler to stop the application while running.
    #
    cherrypy.engine.signals.subscribe()

    #
    # Initialize tools
    #
    cherrypy.tools.db = DatabaseTool()
    authentication_methods = [
        auth_methods.HttpBasicAuthenticationMethod(),
        auth_methods.HttpSessionAuthenticationMethod(),
        auth_methods.HttpJwtAuthenticationMethod()
    ]
    cherrypy.tools.auth = cherrypy.Tool(
        'before_handler',
        CherryPyAuthenticator(authentication_methods)
    )

    #
    # Start the engine.
    #
    cherrypy.engine.start()
    cherrypy.engine.block()

    return 0


def error_page_400(status, message, traceback, version): \
        # pylint: disable=unused-argument
    cherrypy.response.headers['Content-Type'] = 'application/json'
    return json.dumps(TortugaController(app).errorResponse(message))


def error_page_404(status, message, traceback, version): \
        # pylint: disable=unused-argument
    cherrypy.response.headers['Content-Type'] = 'application/json'
    return json.dumps(
        TortugaController(app).errorResponse(message, http_status=404))


def handle_error():
    cherrypy.response.headers['Content-Type'] = 'application/json'
    return json.dumps(TortugaController(app).errorResponse(
        'Internal error', http_status=500))


def main():
    p = argparse.ArgumentParser()

    wsPort = app.cm.getAdminPort()

    p.add_argument('-d', action="store_true",
                   dest='daemonize', help="run the server as a daemon")

    p.add_argument('--debug', action="store_true",
                   default=False, help="Enable debug mode")

    p.add_argument('--pidfile',
                   dest='pidfile', default='/var/run/tortugawsd.pid',
                   help="store the process id in the given file")

    p.add_argument('-c', '--ssl-cert', default=None,
                   dest="sslCert",
                   help=("Path to the SSL certificate to use. "
                         "--ssl-key is also required for SSL operation."))

    p.add_argument('-k', '--ssl-key', default=None,
                   dest="sslKey",
                   help=("Path to the SSL key to use. --ssl-cert "
                         "is also required for SSL operation."))

    p.add_argument('-l', '--listen', default='0.0.0.0',
                   help='IP address to listen on (default: %default)')

    p.add_argument('-p', '--port', type=int, default=wsPort,
                   help="Port to listen on (default: %default)")

    args = p.parse_args()

    if os.path.exists(args.pidfile):
        with open(args.pidfile) as fp:
            pid = fp.read().rstrip()
            if pid:
                if os.access('/proc/{0}'.format(pid), os.F_OK):
                    sys.stderr.write(
                        'tortugawsd is already running (pid: {})\n'.format(
                            pid))

                    sys.exit(1)

    prepare_server()

    cfgdict = {
        'server.socket_host': args.listen,
        'server.socket_port': args.port,
        'log.access_file': '/var/log/tortugaws_access_log',
        'log.error_file': '/var/log/tortugaws_error_log',
        'request.error_response': handle_error,
        'error_page.400': error_page_400,
        'error_page.404': error_page_404,
        'tools.sessions.on': True,
        'tools.auth.on': True,
    }

    if not args.debug:
        cfgdict['environment'] = 'production'

    cherrypy.config.update(cfgdict)

    if args.sslCert and args.sslKey:
        # Enable SSL
        cherrypy.config.update({
            'server.ssl_module': 'builtin',
            'server.ssl_certificate_chain': os.path.join(
                app.cm.getEtcDir(), 'CA/ca.pem'),
            'server.ssl_certificate': args.sslCert,
            'server.ssl_private_key': args.sslKey,
        })

    ret = run_server(args.daemonize, args.pidfile, args.debug)

    sys.exit(ret)
