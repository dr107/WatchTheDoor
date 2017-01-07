import os
from logging import Logger

import yagmail
from injector import inject

from app.configurator import AppConfig


class MessageSender(object):
    @inject
    def __init__(self, ac: AppConfig, logger: Logger):
        self.ac = ac
        self.logger = logger

    def _connect(self):
        return yagmail.SMTP(self.ac.email, self.ac.passwd)

    def send(self, attachment, to=None):
        contents = [
            "It seems like someone's at the door, check the attachment",
            attachment
        ]
        with self._connect() as yag:
            send = self.ac.send_to if to is None else [to]
            for email in send:
                self.logger.info("Sending a message to %s" % email)
                yag.send(email, "SOMEONE AT THE DOOR (maybe)", contents)

        os.remove(attachment)
