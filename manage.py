#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AQMS_Python.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    
    
import logging
import json
import time

from oslo.config import cfg
from eventlet import greenthread

from qga_proxy.proxy import QGA

qga_proxy_opts = [
    cfg.IntOpt('http_timeout',
               default=10,
               help='Time out for accessing qga-proxy http API'),
]

CONF = cfg.CONF
CONF.register_opts(qga_proxy_opts, group='qga_proxy')

LOG = logging.getLogger(__name__)


class _Base(object):
    def __init__(self, env):
        self.params = env['eventlet.input'].read()
        self.method = env['REQUEST_METHOD']
        self.timeout = CONF.qga_proxy.http_timeout

        if env.has_key('HTTP_TIMEOUT'):
            try:
                self.timeout = int(env['HTTP_TIMEOUT'])
            except:
                pass

        self.status = 200
        self.result = ''
        if self.method == 'POST':
            try:
                self.result = self.post()
            except Exception, ex:
                LOG.error(str(ex), exc_info=True)
                self.status = 500
                self.result = str(ex)

        if self.method == 'GET':
            try:
                self.result = self.get()
            except Exception, ex:
                LOG.error(str(ex), exc_info=True)
                self.status = 500
                self.result = str(ex)

    def post(self):
        pass

    def get(self):
        pass


class Send(_Base):
    def post(self):
        LOG.info('=' * 20)
        LOG.info('Timeout:%s' % self.timeout)
        LOG.info('Params:%s' % self.params)
        try:
            datas = json.loads(self.params)
        except:
            raise Exception('json format error,must be json.'
                            'please read the API documents carefully!')

        if not isinstance(datas, dict):
            raise Exception('dict format error,must be dict.'
                            'please read the API documents carefully!')

        _commands = dict()
        _request_ids = list()
        for vm_uuid, commands in datas.iteritems():
            for cd in commands:
                try:
                    d = json.loads(cd)
                except:
                    raise Exception('json format error.please read the API documents carefully!')

                if not isinstance(d, dict):
                    raise Exception('dict format error.please read the API documents carefully!')

                if not d.has_key('arguments'):
                    raise Exception('format error,command must have "arguments" param.'
                                    'please read the API documents carefully!')

                if not isinstance(d['arguments'], dict):
                    raise Exception('format error,"arguments" must be a dict.'
                                    'please read the API documents carefully!')

                if not d['arguments'].has_key('id'):
                    raise Exception('format error,command must have "id" param.'
                                    'please read the API documents carefully!')

                _request_ids.append((d['arguments']['id'], vm_uuid))
                if _commands.has_key(vm_uuid):
                    _commands[vm_uuid].append((cd, d['arguments']['id']))
                else:
                    _commands[vm_uuid] = [(cd, d['arguments']['id'])]

        QGA.send_command(_commands)
        _result = list()
        last = time.time()
        while len(_result) != len(_request_ids) and time.time() - last < self.timeout:
            _result.extend([data for data in QGA.get_data(_request_ids)])
            greenthread.sleep(1)

        LOG.info('Return:%s' % _result)
        return json.dumps(_result)


handlers = {
    '': Send,
    '/': Send,
}
