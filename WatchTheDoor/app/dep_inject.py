import atexit
from logging import Logger, getLogger, INFO

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import BaseScheduler
from injector import Module, provider, singleton


class WatchTheDoorModule(Module):
    """
    A module to provide some tailored data to the app's injector.
    """

    @provider
    @singleton
    def new_scheduler(self) -> BaseScheduler:
        """
        Set up a scheduler.
        :return: A scheduler object.
        """
        scheduler = BackgroundScheduler()
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
        return scheduler

    @provider
    @singleton
    def logger(self) -> Logger:
        """
        Set up the logger as we need it.
        :return: the logger
        """
        logger = getLogger("WatchTheDoor")
        logger.setLevel(INFO)
        return logger
