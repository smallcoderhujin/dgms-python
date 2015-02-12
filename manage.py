#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AQMS_Python.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    
    
import os
import sys
import json
import logging

import eventlet

eventlet.monkey_patch()
from eventlet import wsgi
from oslo.config import cfg

from qga_proxy.proxy import QGA
from qga_proxy.common.log_util import init as log_init, verify_log_file, verify_directory
from qga_proxy.api import handlers

reload(sys)
sys.setdefaultencoding('utf8')

qga_proxy_opts = [
    cfg.StrOpt('host',
               default='127.0.0.1',
               help='http host'),
    cfg.IntOpt('port',
               default=8500,
               help='http port'),
    cfg.StrOpt('log_path',
               default='/var/log/qga-proxy',
               help='log path'),
    cfg.StrOpt('log_format',
               default='%Y-%m-%d',
               help='qga socket file name'),
    cfg.StrOpt('log_change_unit',
               default='D',
               help='check new socket file if vm is starting'),
    cfg.IntOpt('log_change_time',
               default=1,
               help='receive data from new sockets'),
    cfg.IntOpt('log_backup_count',
               default=60 * 2,
               help='qga socket timeout'),
]

CONF = cfg.CONF
CONF(default_config_files=['/etc/nova/nova.conf'])
CONF.register_opts(qga_proxy_opts, group='qga_proxy')

qga = QGA()
qga.start()

LOG = logging.getLogger(__name__)


def init():
    verify_directory(CONF.qga_proxy.log_path)
    log_path = os.path.join(CONF.qga_proxy.log_path, 'qga-proxy.log')
    verify_log_file(log_path)
    log_init(log_path, CONF.qga_proxy.log_change_unit, CONF.qga_proxy.log_change_time,
             CONF.qga_proxy.log_format, logging.INFO, CONF.qga_proxy.log_backup_count)


def api_proxy(env, start_response):
    url = env['PATH_INFO']
    if not handlers.has_key(url):
        start_response('404', [('Content-Type', 'text/plain')])
        return json.dumps(dict(error='Not Found'))

    api = handlers[url](env)
    start_response(str(api.status), [('Content-Type', 'text/plain')])
    return api.result


def start():
    init()
    LOG.debug('start http server')
    wsgi.server(eventlet.listen((CONF.qga_proxy.host, CONF.qga_proxy.port)), api_proxy)
