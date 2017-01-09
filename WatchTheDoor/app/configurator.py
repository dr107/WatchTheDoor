from json import load as json_load
from logging import Logger

from injector import singleton, inject
from subprocess import check_output
from os.path import isfile


def _get_host():
    return check_output(["hostname", "-I"], universal_newlines=True).strip().split()[0]


@singleton
class AppConfig(object):
    CREDS_FILE = 'config_secret/creds.json'
    TO_FILE = 'config_secret/to.json'
    PUBLIC_FILE = 'config_public.json'

    @inject
    def __init__(self, logger: Logger):
        self.logger = logger
        self._get_creds()
        self.host = _get_host()
        self._get_job_config()

    def _get_job_config(self):
        with open(AppConfig.PUBLIC_FILE, 'r') as config:
            js = json_load(config)
            self.interval = int(js['interval'])
            self.post_find_interval = int(js['post_find_interval'])
            self.name = str(js['name'])

    def _get_creds(self):
        files_found = True
        if not isfile(AppConfig.CREDS_FILE):
            self.logger.error("You need to create the credentials file at {}".format(AppConfig.CREDS_FILE))
            files_found = False
        if not isfile(AppConfig.TO_FILE):
            self.logger.error("You need to create the recipients file at {}".format(AppConfig.TO_FILE))
            files_found = False

        if not files_found:
            raise FileNotFoundError("Please create the required files. Examples should already exist")

        with open(AppConfig.CREDS_FILE, 'r') as creds:
            js = json_load(creds)
            self.email = str(js["name"])
            self.passwd = str(js["password"])

        with open(AppConfig.TO_FILE, 'r') as to:
            js = json_load(to)
            self.send_to = [str(email) for email in js]
