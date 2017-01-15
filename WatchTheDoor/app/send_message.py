from logging import Logger

import yagmail
from injector import inject

from app.configurator import AppConfig


class MessageSender(object):
    @inject
    def __init__(self, ac: AppConfig, logger: Logger):
        """
        Constructor. Arguments are dependency injected.
        :param ac: app configuration
        :param logger: logger
        """
        self.ac = ac
        self.logger = logger
        self.subject = ac.email_subject
        self.body = ac.email_body

    def _connect(self) -> yagmail.SMTP:
        """
        Create a new yagmail SMTP connection.
        :return: the yagmail SMTP connection
        """
        return yagmail.SMTP(self.ac.email, self.ac.passwd)

    def send(self, attachment: str) -> type(None):
        """
        Send a message containing an attachment to the users configured in the app configuration. The app config also
        specifies the message text
        :param attachment: the full file path of the attachment
        :return: None
        """
        contents = [
            self.body, attachment
        ]
        with self._connect() as yag:
            for email in self.ac.send_to:
                self.logger.info("Sending a message to %s" % email)
                yag.send(email, self.subject, contents)
