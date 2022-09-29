import logging
import logging.handlers
from .config import logCfg
import json
import time
import concurrent.futures
import os
import requests


FORMAT_OPENTELEMTRY = 'open_telemetry'
levels = {
    'TRACE': 1,
    'DEBUG': 5,
    'INFO': 9,
    'WARN': 13,
    'ERROR': 17,
    'FATAL': 21
}

class Logger:
    def __init__(self, name, format=FORMAT_OPENTELEMTRY):
        self.logger = logging.getLogger(name)
        self.format = format


    def log_string(self, message, level, extra):
        if self.format == FORMAT_OPENTELEMTRY:
            log_message = { 
                'Body': message, 
                'Timestamp': int(time.time()),
                'SeverityText': level,
                'SeverityNumber': levels[level]
            }

            if extra:
                log_message['Attributes'] = extra

            return json.dumps(log_message, default=str)
        else:
            if extra:
                log_message = f'{message} : {extra.__str_}'
            else:
                log_message = message

            return log_message


    def log(self, level, message : str, extra : dict = None):
        log_msg = self.log_string(message, level, extra)
        print(log_msg)

    def trace(self, message : str, extra : dict = None ):
        self.log('TRACE', message, extra)

    def debug(self, message : str, extra : dict = None ):
        self.log('DEBUG', message, extra)

    def info(self, message : str, extra : dict = None ):
        self.log('INFO', message, extra)

    def error(self, message : str, extra : dict = None ):
        self.log('ERROR', message, extra)

    def warning(self, message : str, extra : dict = None ):
        self.log('WARN', message, extra)
        
    def fatal(self, message : str, event='', extra : dict = None ):
        self.log('FATAL', message, extra)

# Note: This log handler is not for use outside of local development.
#       Logs are collectd from standard output in openshift pods.
class DataDogLogHandler(logging.StreamHandler):
    """
    Adds properties to route the logs once they get to DataDog and then sends the logs over HTTPS
    """
    def emit(self, record):
        dd_log_cfg = logCfg.datadog['logging']

        if not dd_log_cfg['enabled']:
            return

        api_key = os.environ.get('DD_API_KEY', None)

        if not api_key:
            print("DD_API_KEY not found in env - not sending log")
            return

        request_headers = {
            'Content-Type': 'application/json',
            'DD-API-KEY': api_key,
        }

        json_record = record.__dict__

        if 'msg' in json_record:
            if type(json_record['msg']).__name__ == 'str':
                json_record |= (json.loads(json_record['msg']))
                del json_record['msg']

        concurrent.futures.ProcessPoolExecutor().submit(
            requests.post, dd_log_cfg['intake_url'],
            headers=request_headers,
            json=[json_record]
        )

def get_logger(name):
    logger = Logger(name)
    log = logger.logger

    log.setLevel(logCfg.level)
    log.propagate = False

    handler = logging.StreamHandler()
    handler.setLevel(logCfg.level)

    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    
    return logger

def get_dd_logger(name):
    dd_logger = logging.getLogger(name)
    dd_logger.setLevel(logging.INFO)
    dd_logger.propagate = False
    handler = DataDogLogHandler()
    dd_logger.addHandler(handler)
    return dd_logger

# orignal code for now
log = logging.getLogger(__name__)

log.setLevel(logCfg.level)
log.propagate = False


handler = logging.StreamHandler()
handler.name = "stderr"
handler.setLevel(logCfg.level)

formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


if logCfg.file: 
    file_size = int(logCfg.get('file_size', default=str(1024*1024*10)))
    file_handler = logging.handlers.RotatingFileHandler(logCfg.file, maxBytes=file_size, backupCount=2)
    file_handler.name = "file"
    file_handler.setLevel(logCfg.level)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

def no_stderr():
    log.removeHandler(handler)

