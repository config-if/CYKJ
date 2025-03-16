# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:28
# @Author  : zwj, lyf, lhl
# @File    : processer.py
from cykj.cut import Cutter

import os
# os.environ['CURL_CA_BUNDLE'] = ''
# os.environ["http_proxy"] = "http://127.0.0.1:7890"
# os.environ["https_proxy"] = "http://127.0.0.1:7890"

from autocut import WhisperMode, WhisperModel
from autocut import utils
from cykj.transcribe import Transcribe
import argparse


def create_T():

    parser = argparse.ArgumentParser(
        description="Edit videos based on transcribed subtitles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("inputs", type=str, nargs="+", help="Inputs filenames/folders")
    parser.add_argument(
        "-t",
        "--transcribe",
        help="Transcribe videos/audio into subtitles",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-c",
        "--cut",
        help="Cut a video based on subtitles",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-d",
        "--daemon",
        help="Monitor a folder to transcribe and cut",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-s",
        help="Convert .srt to a compact format for easier editing",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-m",
        "--to-md",
        help="Convert .srt to .md for easier editing",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="zh",
        choices=[
            "zh",
            "en",
            "Afrikaans",
            "Arabic",
            "Armenian",
            "Azerbaijani",
            "Belarusian",
            "Bosnian",
            "Bulgarian",
            "Catalan",
            "Croatian",
            "Czech",
            "Danish",
            "Dutch",
            "Estonian",
            "Finnish",
            "French",
            "Galician",
            "German",
            "Greek",
            "Hebrew",
            "Hindi",
            "Hungarian",
            "Icelandic",
            "Indonesian",
            "Italian",
            "Japanese",
            "Kannada",
            "Kazakh",
            "Korean",
            "Latvian",
            "Lithuanian",
            "Macedonian",
            "Malay",
            "Marathi",
            "Maori",
            "Nepali",
            "Norwegian",
            "Persian",
            "Polish",
            "Portuguese",
            "Romanian",
            "Russian",
            "Serbian",
            "Slovak",
            "Slovenian",
            "Spanish",
            "Swahili",
            "Swedish",
            "Tagalog",
            "Tamil",
            "Thai",
            "Turkish",
            "Ukrainian",
            "Urdu",
            "Vietnamese",
            "Welsh",
        ],
        help="The output language of transcription",
    )
    parser.add_argument(
        "--prompt", type=str, default="", help="initial prompt feed into whisper"
    )
    parser.add_argument(
        "--whisper-mode",
        type=str,
        default=WhisperMode.FASTER.value,
        choices=WhisperMode.get_values(),
        help="Whisper inference mode: whisper: run whisper locally; openai: use openai api.",
    )
    parser.add_argument(
        "--openai-rpm",
        type=int,
        default=3,
        choices=[3, 50],
        help="Openai Whisper API REQUESTS PER MINUTE(FREE USERS: 3RPM; PAID USERS: 50RPM). "
             "More info: https://platform.openai.com/docs/guides/rate-limits/overview",
    )
    parser.add_argument(
        "--whisper-model",
        type=str,
        default=WhisperModel.LARGE.value,
        choices=WhisperModel.get_values(),
        help="The whisper model used to transcribe.",
    )
    parser.add_argument(
        "--bitrate",
        type=str,
        default="10m",
        help="The bitrate to export the cutted video, such as 10m, 1m, or 500k",
    )
    parser.add_argument(
        "--vad", help="If or not use VAD", choices=["1", "0", "auto"], default="auto"
    )
    parser.add_argument(
        "--force",
        help="Force write even if files exist",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--encoding", type=str, default="utf-8", help="Document encoding format"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        choices=["cpu", "cuda"],
        help="Force to CPU or GPU for transcribing. In default automatically use GPU if available.",
    )
    return parser
def runT(args):
    # args_list = ['-t', args, '--whisper-model large']
    args_list = ['-t', args]
    parser = create_T()
    args = parser.parse_args(args_list)
    Transcribe(args).run()


def runC(args, args2):
    args_list = ['-c', args, args2]
    parser = create_T()
    args = parser.parse_args(args_list)
    Cutter(args).run()

if __name__ == "__main__":
    runT("/home/errico/桌面/code903/演示视频/media/interview.mp4")
    # runC("/home/errico/桌面/autocut/media/interview.mp4", "/home/errico/桌面/autocut/media/interview.srt")