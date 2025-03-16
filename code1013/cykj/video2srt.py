# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:31
# @Author  : zwj, lyf, lhl
# @File    : video2srt.py

import argparse
import logging
import os

from . import utils
from .type import WhisperMode, WhisperModel

def transcribe_videos(video):
    logging.basicConfig(
        format="[autocut:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s"
    )
    logging.getLogger().setLevel(logging.INFO)

    if 1:
        from .transcribe import Transcribe

        # Here, we simulate the args object that was previously parsed from the command line
        class Args:
            inputs = video  # You can customize this as needed
            lang = "zh"
            prompt = ""
            whisper_mode = WhisperMode.WHISPER.value
            openai_rpm = 3
            whisper_model = WhisperModel.SMALL.value
            bitrate = "10m"
            vad = "auto"
            force = False
            encoding = "utf-8"
            device = None

        args = Args()
        Transcribe(args).run()
    else:
        logging.warning("No action, use -t to transcribe videos")


