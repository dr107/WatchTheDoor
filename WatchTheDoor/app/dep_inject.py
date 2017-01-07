import atexit

from logging import Logger, getLogger, INFO

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import BaseScheduler
from injector import Module, provider, singleton


class WatchTheDoorModule(Module):
    @provider
    @singleton
    def new_scheduler(self) -> BaseScheduler:
        scheduler = BackgroundScheduler()
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
        return scheduler

    @provider
    @singleton
    def logger(self) -> Logger:
        logger = getLogger("WatchTheDoor")
        logger.setLevel(INFO)
        logger.info("Logger setup complete")
        return logger
