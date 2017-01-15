import os
from logging import Logger
from typing import Optional
from urllib.request import urlopen
from uuid import uuid4

import cv2
import numpy as np
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.interval import IntervalTrigger
from injector import inject, singleton

from app.configurator import AppConfig
from app.send_message import MessageSender


@singleton
class Detector(object):
    _JOB_NAME = 'DETECT_JOB'

    @inject
    def __init__(self, ac: AppConfig, sender: MessageSender, scheduler: BaseScheduler, logger: Logger):
        """
        Constructor. Arguments are meant to be dependency injected.
        :param ac: app configuration
        :param sender: message sender module
        :param scheduler: Scheduler
        :param logger: logger
        """
        self.config = ac
        self.sender = sender
        self.scheduler = scheduler
        self.trigger = IntervalTrigger(seconds=self.config.interval)
        self.post_find_trigger = IntervalTrigger(seconds=self.config.post_find_interval)
        casc_path = "/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml"
        self.face_casc = cv2.CascadeClassifier(casc_path)
        self.logger = logger

    def launch_detect_job(self) -> type(None):
        """
        Kick off the face detection job with configuration as specified by the app config in the input
        :return: the scheduler job created by kicking this off
        """
        self.logger.info("launching teh job")
        return self.scheduler.add_job(
            func=self._take_pic,
            trigger=self.trigger,
            id=Detector._JOB_NAME,
            name="Detect faces at the door",
            replace_existing=True
        )

    @staticmethod
    def _fetch_image_bytes() -> np.ndarray:
        """
        Fetch a snapshot from the UV4L server and return it as a numpy byte array.
        :return: the image fetched as a numpy byte array
        """
        resp = urlopen("http://localhost:8080/stream/snapshot.jpeg").read()
        return np.asarray(bytearray(resp), dtype=np.uint8)

    def _detect_faces(self) -> Optional[str]:
        """
        Fetch an image from the uv4l server, inspect it for faces, and return the number of faces found, and a saved
        image with the faces boxed in, if one or more is found
        :return: the file name of an image containing faces, if any were found. Otherwise, return None.
        """
        return self._detect(Detector._fetch_image_bytes())

    def _take_pic(self) -> type(None):
        """
        The job function. Does everything.
        :return: None
        """
        name = self._detect_faces()
        job = self.scheduler.get_job(Detector._JOB_NAME)
        if name is not None:
            self.sender.send(name)
            self.logger.info("Deleting attachment file {}".format(name))
            os.remove(name)
            self.logger.info("Rescheduling the job as specified by the post find interval")
            job.reschedule(self.post_find_trigger)
        elif job.trigger != self.trigger:
            self.logger.info("Rescheduling the job as normal!")
            job.reschedule(self.trigger)

    def _detect(self, img_bytes: np.ndarray) -> Optional[str]:
        """
        Detect faces in an image. Return the number of the file path of an image
        :param img_bytes: a numpy array representing an image which may or may not have a face.
        :return: the file name of an image with faces highlighted, if any faces were found. If not, return null.
        """
        img = cv2.imdecode(img_bytes, -1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_casc.detectMultiScale(
            # here's where the tweaking happens
            gray,
            scaleFactor=1.01,
            minNeighbors=5,
            minSize=(100, 100),
            flags=cv2.CV_FEATURE_PARAMS_HAAR
        )

        num_faces = len(faces)
        self.logger.info("Found {:d} faces".format(num_faces))

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            self.logger.info("Found face with width={:d} height={:d}".format(w, h))
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if num_faces == 0:
            return None

        # the massive cardinality of the uuid space makes a collision nearly impossible
        name = '/tmp/{}.png'.format(uuid4())
        cv2.imwrite(name, img)
        self.logger.info("Image file written to {}".format(name))
        return name
