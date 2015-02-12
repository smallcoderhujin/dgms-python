#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AQMS_Python.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
    
    
import logging
import sys
import os

from logging.handlers import TimedRotatingFileHandler


def verify_directory(dirpath):
    if os.path.exists(dirpath):
        if os.path.isdir(dirpath):
            return
        sys.stderr.write("%s is not a directory\n" % dirpath)
        sys.exit(1)

    try:
        os.makedirs(dirpath, 0700)
    except OSError, e:
        sys.stderr.write("create directory %s failed: %s\n" % (dirpath, e.strerror))
        sys.exit(1)


def verify_log_file(logfile):
    try:
        with open(logfile, 'a'):
            pass
    except IOError, e:
        sys.stderr.write("open %s failed: %s\n" % (logfile, e.strerror))


def init(log_name, tp, tp_count, suffix, level, backup=0, LOG=None):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.handlers.TimedRotatingFileHandler(
        log_name,
        when=tp,
        interval=tp_count,
        backupCount=backup)
    handler.suffix = suffix
    handler.setFormatter(formatter)

    logging.root.addHandler(handler)
    logging.root.setLevel(level)
