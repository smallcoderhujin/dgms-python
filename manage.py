#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AQMS_Python.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    
    
import json

import httplib

HOST = '127.0.0.1'
PORT = '8500'


def post(host, port, api, data):
    conn = httplib.HTTPConnection(host, port)
    conn.request("POST", api, data)
    return conn.getresponse()


def get(host, port, api, params=None):
    conn = httplib.HTTPConnection(host, port)

    conn.request("GET", api, params)
    return conn.getresponse()


def input_data():
    commands = []
    uuid = raw_input('Please input uuid:')
    while True:
        commands.append(json.dumps(json.loads(raw_input('Input command:'))))
        again = input('Continue[1]')
        if again != 1:
            break
    return uuid, commands


def main():
    print 'Send Data'
    datas = dict()
    while True:
        uuid, commands = input_data()
        again = input('OK[1],Cancel[0]:')
        if again == 1:
            datas[uuid] = commands

        again = input('Continue[1],Send[2]:')
        if again == 2:
            break

    result = post(HOST, PORT, '/', json.dumps(datas))
    print result.read()
    main()


if __name__ == '__main__':
    main()
