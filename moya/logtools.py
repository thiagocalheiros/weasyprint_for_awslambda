from __future__ import print_function
from __future__ import unicode_literals

from . import pilot
from .console import ConsoleHighlighter

import os
import sys
import io
import logging
import logging.handlers


runtime_log = logging.getLogger('moya.runtime')


class LogHighlighter(ConsoleHighlighter):
    styles = {
        None: "cyan",
        "tag": "yellow not bold",
        "debug": "dim green",
        "info": "green",
        "warning": "red",
        "error": "bold red",
        "critical": "bold red reverse",
        "logdate": "blue",
        "string_single": "green",
        "string_double": "green",
        "get": "bold magenta",
        "head": "bold cyan",
        "post": "bold blue",
        "method": "bold",
        "errorresponse": "bold red",
        "responsecode": "not dim",
        "path": "bold blue",
        #"dim": "dim",
        "url": "underline",
        #"parenthesis": "dim"
    }

    highlights = [
        r'(?P<path>\s\/[-_\.\w\/]*)',
        r'(?P<tag>\<.*?\>)',

        r'^(?P<logdate>\[.*?\])',
        r'(?P<string_single>\".*?\")|(?P<string_double>\'.*?\')',

        r'^\[.*\](?P<info>:.*?:INFO:)',
        r'^\[.*\](?P<debug>:.*?:DEBUG:)',
        r'^\[.*\](?P<warning>:.*?:WARNING:)',
        r'^\[.*\](?P<error>:.*?:ERROR:)',
        r'^\[.*\](?P<critical>:.*?:CRITICAL:)',

        r'(?P<request>\".*?\") (?:(?P<errorresponse>[45]\S+)|(?P<responsecode>\S+))',
        r'(?P<method>\"(?:OPTIONS|DELETE|TRACE|CONNECT) .*?\")',

        r'(?P<get>\"GET .*?\")',
        r'(?P<head>\"HEAD .*?\")',
        r'(?P<post>\"POST .*?\")',

        r'(?P<url>https{0,1}://[a-zA-Z0-9\.\%\:\/\-]*)[\s\'\"$]?',
        r'(?P<parenthesis>\(.*?\))'
    ]


class MoyaConsoleHandler(logging.StreamHandler):
    """A handler that writes colored output to the console"""

    def emit(self, record):
        text = self.format(record)
        htext = LogHighlighter.highlight(text)
        pilot.console(htext).nl()


class MoyaFileHandler(logging.Handler):
    """
    A handler that writes to a file.

    The default FileHandler keeps the file open, which breaks when Ubuntu rotates the logs. This handler
    avoids that issue by closing the file on every emit.

    """

    def __init__(self, filename):
        self._filename = filename
        self._access_check = False
        super(MoyaFileHandler, self).__init__()

    def emit(self, record):
        text = self.format(record)
        try:
            with io.open(self._filename, 'at', encoding="utf-8") as f:
                f.write(text + '\n')
        except Exception as error:
            # Check if it was permissions related
            if not self._access_check:
                self._access_check = True
                if not os.access(self._filename, os.W_OK):
                    self._access_check = True
                    runtime_log.error(
                        "no permission to write to log file '%s'",
                        self._filename
                    )
                else:
                    runtime_log.error(
                        "unable to write to log file '%s' (%s)'",
                        self._filename,
                        error
                    )



class MoyaSysLogHandler(logging.handlers.SysLogHandler):
    """
    A syslog handler that detects the platform

    """
    def __init__(self):
        platform = sys.platform
        if platform == 'linux2':
            args = ('/dev/log',)
        elif platform == 'darwin':
            args = ('/var/run/syslog',)
        elif platform == 'win32':
            args = ()
        else:
            args = ()
        super(MoyaSysLogHandler, self).__init__(*args)


class LoggerFile(object):
    """A file-like object that writes to a log"""

    def __init__(self, logger):
        self._logger = logger
        self._log = logging.getLogger(logger)
        self._text = []

    def __repr__(self):
        return "<loggerfile '{}'>".format(self._logger)

    def write(self, text):
        self._text.append(text)
        if '\n' in text:
            lines = ''.join(self._text).splitlines(True)
            for i, line in enumerate(lines):
                if line.endswith('\n'):
                    self._log.info(line[:-1])
                else:
                    self._text[:] = lines[i:]
                    break
            else:
                del self._text[:]

    def flush(self):
        pass

    def isatty(self):
        return False


class MoyaServiceFormatter(logging.Formatter):

    def format(self, record):

        log_msg = super(MoyaServiceFormatter, self).format(record)

        project = getattr(record, 'project', None)
        if project is None:
            project = pilot.service.get('name')

        if project is not None:
            project_prefix = "({})".format(project).ljust(14)
        else:
            project_prefix = " " * 14
        log_msg = "{}{}".format(project_prefix, log_msg)
        return log_msg
