#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AQMS_Python.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    
    
import os
import logging

import eventlet

eventlet.monkey_patch()
from oslo.config import cfg

from qga_proxy.proxy import QGA
from qga_proxy.common.log_util import init as log_init, verify_log_file, verify_directory

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

LOG = logging.getLogger(__name__)


def init():
    verify_directory(CONF.qga_proxy.log_path)
    log_path = os.path.join(CONF.qga_proxy.log_path, 'qga-proxy.log')
    verify_log_file(log_path)
    log_init(log_path, CONF.qga_proxy.log_change_unit, CONF.qga_proxy.log_change_time,
             CONF.qga_proxy.log_format, logging.DEBUG, CONF.qga_proxy.log_backup_count)


def start_qga():
    qga = QGA()
    qga.start()


def start():
    commands = dict()
    commands['instance-000001bb'] = [('{"execute":"guest-get-service-info", "arguments":{"id":"%s"}}' % 'qga1', 'qga1')]
    commands['instance-00000202'] = [('{"execute":"guest-get-process-info", "arguments":{"id":"%s"}}' % 'qga2', 'qga2')]

    QGA.send_command(commands)
    for i in QGA.get_data(['qga1', 'qga2']):
        print i
