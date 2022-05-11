#/usr/bin/env python3

# Authored by: Bitraker

import linecache # Logger
import time # Logger
import sys # Logger
from datetime import datetime as dt

class Logger:

    """ Logger class supporting different log levels; info, debug, warning """

    def __init__(self,
        severity=7,
        log_filepath=None):
        self.log_filepath = log_filepath
        self.severity = severity
        self.severity_names = {
            0:"emergency",
            1:"alert",
            2:"critical",
            3:"error",
            4:"warning",
            5:"notice",
            6:"informational",
            7:"debug"
        }

    def _rfc5424_timestamp_utc(self):
        return dt.strftime(dt.utcnow(), "%Y-%m-%dT%H:%M:%S.%f")

    def _rfc5424_msg(self, msg):
        return msg

    def _construct_msg(self, msg, severity):
        return f"{self._rfc5424_timestamp_utc()} {self.severity_names[severity]} {self._rfc5424_msg(msg)}"

    def _write_to_logfile(self, line):
        if self.log_filepath:
            with open(self.log_filepath, 'a') as f:
                f.write(f'{line}\n')

    def emergency(self, msg):
        message = self._construct_msg(msg, 0)
        if self.severity >= 0:
            self._write_to_logfile(message)

    def alert(self, msg):
        message = self._construct_msg(msg, 1)
        if self.severity >= 1:
            self._write_to_logfile(message)

    def exception(self):
        message = self._construct_msg(self.line_exception(), 2)
        if self.severity >= 3:
            self._write_to_logfile(message)

    def error(self, msg):
        message = self._construct_msg(msg, 3)
        if self.severity >= 3:
            self._write_to_logfile(message)

    def warning(self, msg):
        message = self._construct_msg(msg, 4)
        if self.severity >= 4:
            self._write_to_logfile(message)

    def notice(self, msg):
        message = self._construct_msg(msg, 5)
        if self.severity >= 5:
            self._write_to_logfile(message)

    def info(self, msg):
        message = self._construct_msg(msg, 6)
        if self.severity >= 6:
            self._write_to_logfile(message)

    def debug(self, msg):
        message = self._construct_msg(msg, 7)
        if self.severity == 7:
            self._write_to_logfile(message)

    def line_exception(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        return f"exception in {filename} at {lineno}: {line.strip()}: {exc_obj}"