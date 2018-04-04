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

import os.path
import sys
from optparse import OptionParser
import json
from pathlib import Path
import logging
import logging.config
import logging.handlers

import cherrypy
from cherrypy.process import plugins
from sqlalchemy.orm import scoped_session, sessionmaker
from tortuga.web_service import adminRouteMapper
from tortuga.web_service.workQueuePlugin import WorkQueuePlugin
from tortuga.web_service.controllers.tortugaController \
    import TortugaController
from tortuga.web_service.threadManagerPlugin import ThreadManagerPlugin
from . import app, dbm


# read logging configuration
log_conf_file = Path(app.cm.getEtcDir()) / 'tortugawsd.log.conf'
if log_conf_file.exists():
    logging.config.fileConfig(str(log_conf_file))

# Log everything 'tortuga.*'
root_logger = logging.getLogger('tortuga')

if not log_conf_file.exists():
    # in the absence of a `tortugawsd` logging configuration, use
    # sane defaults
    root_logger.setLevel(logging.DEBUG)

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

logger = logging.getLogger('tortuga.web_service')


def prepareServer():
    """ Prepare server. """
    logger.debug('Loading service configuration')

    config = {
        '/': {
            'tools.db.on': True,
        },
        '/v1': {
            'request.dispatch': adminRouteMapper.setupRoutes()
        }
    }

    # No root controller as we provided our own.
    return cherrypy.tree.mount(root=None, config=config)


def runServer(daemonize=False, pidfile=None):
    logger.debug('Starting service')

    # Set up daemonization
    if daemonize:
        # Don't print anything to stdout/sterr.
        plugins.Daemonizer(cherrypy.engine).subscribe()

    # Add workqueue plugin
    WorkQueuePlugin(cherrypy.engine).subscribe()

    # Add-nodes workflow
    ThreadManagerPlugin(cherrypy.engine).subscribe()

    if pidfile:
        plugins.PIDFile(cherrypy.engine, pidfile).subscribe()

    # Setup the signal handler to stop the application while running.
    cherrypy.engine.signals.subscribe()

    DatabaseEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = DatabaseTool()

    # Start the engine.
    try:
        cherrypy.engine.start()
        cherrypy.engine.block()
    except Exception:
        logger.exception('Service exiting')

        return 1

    return 0


def error_page_400(status, message, traceback, version): \
        # pylint: disable=unused-argument
    cherrypy.response.headers['Content-Type'] = 'application/json'
    response = TortugaController().errorResponse(message)
    return json.dumps(response)


def handle_error():
    cherrypy.response.headers['Content-Type'] = 'application/json'
    cherrypy.response.status = 500
    return json.dumps(TortugaController().errorResponse('Internal error'))


class DatabaseEnginePlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        super(DatabaseEnginePlugin, self).__init__(bus)

        self.sa_engine = None

        self.bus.subscribe('bind', self.bind)

    def start(self):
        self.sa_engine = dbm.engine

    def stop(self):
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None

    def bind(self, session):
        session.configure(bind=self.sa_engine)


class DatabaseTool(cherrypy.Tool):
    def __init__(self):
        super(DatabaseTool, self).__init__(
            'on_start_resource', self.bind_session, priority=20)

        self.session = scoped_session(sessionmaker(autoflush=True,
                                                   autocommit=False))

    def _setup(self):
        super(DatabaseTool, self)._setup()

        cherrypy.request.hooks.attach('on_end_resource',
                                      self.commit_transaction,
                                      priority=80)

    def bind_session(self):
        cherrypy.engine.publish('bind', self.session)

        cherrypy.request.db = self.session

    def commit_transaction(self):
        cherrypy.request.db = None

        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.remove()


def main():
    p = OptionParser()

    wsPort = app.cm.getAdminPort()

    p.add_option('-d', action="store_true",
                 dest='daemonize', help="run the server as a daemon")

    p.add_option('--debug', action="store_true",
                 default=False, help="Enable debug mode")

    p.add_option('--pidfile',
                 dest='pidfile', default='/var/run/tortugawsd.pid',
                 help="store the process id in the given file")
    p.add_option('-c', '--ssl-cert', default=None,
                 dest="sslCert",
                 help=("Path to the SSL certificate to use. "
                       "--ssl-key is also required for SSL operation."))
    p.add_option('-k', '--ssl-key', default=None,
                 dest="sslKey",
                 help=("Path to the SSL key to use. --ssl-cert "
                       "is also required for SSL operation."))
    p.add_option('-l', '--listen', default='0.0.0.0',
                 help='IP address to listen on (default: %default)')
    p.add_option('-p', '--port', type=int, default=wsPort,
                 help="Port to listen on (default: %default)")

    options, args = p.parse_args()

    if os.path.exists(options.pidfile):
        with open(options.pidfile) as fp:
            pid = fp.read().rstrip()
            if pid:
                if os.access('/proc/{0}'.format(pid), os.F_OK):
                    sys.stderr.write(
                        'tortugawsd is already running (pid: {})\n'.format(pid))

                    sys.exit(1)

    prepareServer()

    cfgdict = {
        'server.socket_host': options.listen,
        'server.socket_port': options.port,
        'log.access_file': '/var/log/tortugaws_access_log',
        'log.error_file': '/var/log/tortugaws_error_log',
        'request.error_response': handle_error,
        'error_page.400': error_page_400,
        'tools.sessions.on': True,
        'tools.auth.on': True,
    }

    if not options.debug:
        cfgdict['environment'] = 'production'

    cherrypy.config.update(cfgdict)

    if options.sslCert and options.sslKey:
        # Enable SSL
        cherrypy.config.update({
            'server.ssl_module': 'builtin',
            'server.ssl_certificate_chain': os.path.join(
                app.cm.getEtcDir(), 'CA/ca.pem'),
            'server.ssl_certificate': options.sslCert,
            'server.ssl_private_key': options.sslKey,
        })

    ret = runServer(options.daemonize, options.pidfile)

    sys.exit(ret)
