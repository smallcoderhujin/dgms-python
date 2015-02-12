#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AQMS_Python.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    
    
import logging
import socket
import os
import json
import time
import random

import libvirt
from libvirt import libvirtError
import eventlet
from eventlet import GreenPile, GreenPool
from eventlet import greenthread

eventlet.monkey_patch()
from oslo.config import cfg

from nova.openstack.common.threadgroup import ThreadGroup

qga_proxy_opts = [
    cfg.StrOpt('socket_dir',
               default='/var/lib/libvirt/qemu/',
               help='qga socket file dir'),
    cfg.StrOpt('socket_file',
               default='%s.agent',
               help='qga socket file name'),
    cfg.IntOpt('check_socket_interval',
               default=10,
               help='check new socket file if vm is starting'),
    cfg.IntOpt('receive_socket_interval',
               default=10,
               help='receive data from new sockets'),
    cfg.IntOpt('socket_timeout',
               default=2,
               help='qga socket timeout'),
    cfg.IntOpt('green_pool_size',
               default=10000,
               help='qga socket timeout'),
    cfg.IntOpt('clear_memory_interval',
               default=60 * 60 * 24 * 1,
               help='clear_memory_interval'),
    cfg.IntOpt('clear_memory_time',
               default=60 * 60 * 24 * 1,
               help='clear_memory_time'),
    cfg.StrOpt('libvirt_url',
               default='qemu:///system',
               help='libvirt url'),
    cfg.IntOpt('reget_vm_list_count',
               default=5,
               help='reget vm list count'),
]

CONF = cfg.CONF
CONF.register_opts(qga_proxy_opts, group='qga_proxy')

SOCKET_DICT = dict()
RECEIVE_DATA_DICT = dict()
RECEIVE_TASK_LIST = list()
TEST_ID_DICT = dict()
QGA_STATE = {'running': 1, 'stopped': 0}

LOG = logging.getLogger(__name__)


class QGA(object):
    def __init__(self, socket_path=CONF.qga_proxy.socket_dir,
                 socket_check_interval=CONF.qga_proxy.check_socket_interval,
                 socket_receive_interval=CONF.qga_proxy.receive_socket_interval,
                 green_pool_size=CONF.qga_proxy.green_pool_size,
                 libvirt_url=CONF.qga_proxy.libvirt_url,
                 socket_timeout=CONF.qga_proxy.socket_timeout,
                 socket_file_name=CONF.qga_proxy.socket_file,
                 clear_memory_interval=CONF.qga_proxy.clear_memory_interval,
                 clear_memory_time=CONF.qga_proxy.clear_memory_time,
                 reget_vm_list_count=CONF.qga_proxy.reget_vm_list_count):
        self._socket_path = socket_path
        self._socket_check_interval = socket_check_interval
        self._socket_receive_interval = socket_receive_interval
        self._green_pool_size = green_pool_size
        self._libvirt_url = libvirt_url
        self._socket_timeout = socket_timeout
        self._socket_file_name = socket_file_name
        self._clear_memory_interval = clear_memory_interval
        self._clear_memory_time = clear_memory_time
        self._reget_vm_list_count = reget_vm_list_count

        self.pool = GreenPool(self._green_pool_size)
        self.pile = GreenPile(self.pool)

        self.vm_uuid_list = set()

    def _get_vm_list(self):
        reget_vm_count = self._reget_vm_list_count
        while reget_vm_count > 0:
            try:
                conn = libvirt.open(self._libvirt_url)
                self.vm_uuid_list = set([vm.UUIDString() for vm in conn.listAllDomains(1)])
                conn.close()
                break
            except libvirtError, ex:
                LOG.error(str(ex), exc_info=True)
            reget_vm_count -= 1

        LOG.debug('vm list:%s' % str(self.vm_uuid_list))

    def _get_vm_socket_path(self, vm_uuid):
        vm_socket_path = self._socket_file_name % vm_uuid
        return os.path.join(self._socket_path, vm_socket_path)

    def _connect_socket(self, path, vm_uuid):
        global SOCKET_DICT, RECEIVE_DATA_DICT
        sock = socket.socket(socket.AF_UNIX)
        try:
            sock.settimeout(self._socket_timeout)
            sock.connect(path)
            SOCKET_DICT[vm_uuid] = {'socket': sock, 'state': QGA_STATE['stopped']}
        except socket.error, ex:
            LOG.warning('socket connect fail.reason:%s.vm_uuid:%s' % (str(ex), os.path.basename(path)))
        except Exception, ex:
            LOG.error(str(ex), exc_info=True)

    def _get_socket_list(self):
        global SOCKET_DICT, RECEIVE_TASK_LIST, TEST_ID_DICT
        _tasks = []
        for vm_uuid in SOCKET_DICT.keys():
            if vm_uuid not in self.vm_uuid_list:
                sock = SOCKET_DICT.get(vm_uuid, None)
                if sock and hasattr(sock, 'close'):
                    sock.close()
                del SOCKET_DICT[vm_uuid]

                if TEST_ID_DICT.has_key(vm_uuid):
                    del TEST_ID_DICT[vm_uuid]

        for vm_uuid in RECEIVE_TASK_LIST:
            if vm_uuid not in self.vm_uuid_list:
                RECEIVE_TASK_LIST.remove(vm_uuid)

        new_vm_uuid_list = list(self.vm_uuid_list - set(SOCKET_DICT.keys()))
        for vm_uuid in new_vm_uuid_list:
            _tasks.append(self.pile.spawn(self._connect_socket, *[self._get_vm_socket_path(vm_uuid), vm_uuid]))

        for p in _tasks:
            pass

    def _test_socket(self):
        global SOCKET_DICT, TEST_ID_DICT, RECEIVE_TASK_LIST
        for vm_uuid in SOCKET_DICT.keys():
            if SOCKET_DICT[vm_uuid]['state'] == QGA_STATE['running']:
                continue

            if TEST_ID_DICT.has_key(vm_uuid):
                continue

            if vm_uuid not in RECEIVE_TASK_LIST:
                continue

            while True:
                test_uuid = int(random.random() * 10000)
                if test_uuid not in TEST_ID_DICT.values():
                    TEST_ID_DICT[vm_uuid] = test_uuid
                    break

            self.send_command({vm_uuid: [('{"execute":"guest-sync","arguments":{"id":%s}}' % test_uuid, test_uuid)]},
                              test_socket=True)
        LOG.debug('vm socket list:%s' % str(
            [vm_uuid for vm_uuid in SOCKET_DICT.keys() if SOCKET_DICT[vm_uuid]['state'] == QGA_STATE['running']]))

    def check_socket_list(self):
        self._get_vm_list()
        self._get_socket_list()
        self._test_socket()

    @staticmethod
    def send_command(command_dict=dict(), test_socket=False):
        LOG.info('send commands:%s' % str(command_dict))

        global SOCKET_DICT
        for vm_uuid, commands in command_dict.iteritems():
            now = int(time.time())
            if not SOCKET_DICT.has_key(vm_uuid):
                for command, id in commands:
                    RECEIVE_DATA_DICT[id] = {'info': {
                        'return': {'msg': 'vm:%s does not have a correct socket connector' % vm_uuid, 'id': id,
                                   'state': 0}}, 'timestamps': now, 'vm': vm_uuid}
                continue

            if not test_socket:
                if SOCKET_DICT[vm_uuid]['state'] == QGA_STATE['stopped']:
                    for command, id in commands:
                        RECEIVE_DATA_DICT[id] = {'info': {
                            'return': {'msg': 'qga of vm:%s is not running' % vm_uuid, 'id': id,
                                       'state': 'qga_downtime'}}, 'timestamps': now, 'vm': vm_uuid}
                    continue

            sock = SOCKET_DICT[vm_uuid]['socket']
            for command, id in commands:
                try:
                    sock.sendall(command)
                except Exception, ex:
                    print ex
                    if SOCKET_DICT.has_key(vm_uuid):
                        del SOCKET_DICT[vm_uuid]
                    break

    def _receive_data(self, vm_uuid):
        LOG.info('receiving from vm:%s ...' % vm_uuid)

        global SOCKET_DICT, RECEIVE_DATA_DICT, RECEIVE_TASK_LIST, TEST_ID_DICT
        if not SOCKET_DICT.has_key(vm_uuid):
            LOG.error('vm:%s does not have a correct socket connected' % vm_uuid)
            return

        sock = SOCKET_DICT[vm_uuid]['socket']
        while True:
            try:
                response = sock.recv(4096)
                if not response:
                    raise Exception('vm:%s socket disconnect' % vm_uuid)

                SOCKET_DICT[vm_uuid]['state'] = QGA_STATE['running']
                responses = response.split('\n')
                for response in responses:
                    if not response:
                        continue

                    LOG.info('receive data:%s' % response)

                    try:
                        response = json.loads(response)
                    except ValueError, ex:
                        LOG.warning(str(ex))
                        continue

                    if not isinstance(response, dict):
                        LOG.warning('qga return is not a dict.response:%s' % str(response))
                        continue

                    if response.has_key('error'):
                        LOG.warning('qga error:%s' % response['error'])
                        continue

                    if not response.has_key('return'):
                        LOG.warning('qga format error,have not a "return" key')
                        continue

                    return_value = response['return']
                    if not isinstance(return_value, dict):
                        LOG.warning('qga format error,return value is not a dict')
                        continue

                    if not return_value.has_key('id'):
                        LOG.warning('qga return value have not a "id" key')
                        continue

                    id = return_value['id']
                    RECEIVE_DATA_DICT[id] = {'info': response, 'timestamps': int(time.time()), 'vm': vm_uuid}
                greenthread.sleep(1)
            except socket.timeout:
                pass
            except RuntimeError, ex:
                LOG.debug(str(ex))
                greenthread.sleep(1)
            except Exception, ex:
                if str(ex) != '[Errno 9] Bad file descriptor':
                    LOG.error(str(ex), exc_info=True)

                if SOCKET_DICT.has_key(vm_uuid):
                    if hasattr(sock, 'close'):
                        sock.close()
                    del SOCKET_DICT[vm_uuid]

                if TEST_ID_DICT.has_key(vm_uuid):
                    del TEST_ID_DICT[vm_uuid]

                if vm_uuid in RECEIVE_TASK_LIST:
                    RECEIVE_TASK_LIST.remove(vm_uuid)
                break

    def receive_data(self):
        global SOCKET_DICT, RECEIVE_TASK_LIST
        _tasks = []
        try:
            for vm_uuid in SOCKET_DICT.keys():
                if vm_uuid not in RECEIVE_TASK_LIST:
                    _tasks.append(self.pile.spawn(self._receive_data, *[vm_uuid]))
                    RECEIVE_TASK_LIST.append(vm_uuid)
        except Exception, ex:
            LOG.error(str(ex), exc_info=True)

        for p in _tasks:
            pass

        LOG.debug('current receive task list:%s' % str(RECEIVE_TASK_LIST))

    @staticmethod
    def get_data(request_ids):
        global RECEIVE_DATA_DICT, SOCKET_DICT
        keys = RECEIVE_DATA_DICT.keys()
        for id, vm_uuid in request_ids:
            if id in keys:
                r = RECEIVE_DATA_DICT[id]['info']
                del RECEIVE_DATA_DICT[id]
                yield r
                continue

            if not SOCKET_DICT.has_key(vm_uuid):
                yield {'return': {'msg': 'vm:%s does not have a correct socket connector' \
                                         % vm_uuid, 'id': id, 'state': 0}}
                continue

            if SOCKET_DICT[vm_uuid]['state'] == QGA_STATE['stopped']:
                yield {'return': {'msg': 'qga of vm:%s is not running' \
                                         % vm_uuid, 'id': id, 'state': 'qga_downtime'}}
                continue

    def clear_memory(self):
        global RECEIVE_DATA_DICT
        for key in RECEIVE_DATA_DICT.keys():
            value = RECEIVE_DATA_DICT[key]
            if not isinstance(value, dict):
                LOG.error('RECEIVE_DATA_DICT type error,info must be dict type')
                del RECEIVE_DATA_DICT[key]
                continue

            if not value.has_key('timestamps'):
                LOG.error('RECEIVE_DATA_DICT format error,must have timestamps')
                del RECEIVE_DATA_DICT[key]
                continue

            if value['timestamps'] < time.time() - self._clear_memory_time:
                del RECEIVE_DATA_DICT[key]

    def start(self):
        tg = ThreadGroup()
        tg.add_timer(self._clear_memory_interval, self.clear_memory)
        tg.add_timer(self._socket_check_interval, self.check_socket_list)
        tg.add_timer(self._socket_receive_interval, self.receive_data)
        tg.add_timer(604800, lambda: None)
