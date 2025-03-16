# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:14
# @Author  : zwj, lyf, lhl
# @File    : pack.py
from PyInstaller.__main__ import run
import os

if __name__ == '__main__':
    os.environ['QT_QPA_PLATFORM'] = 'xcb'  # 设置为 xcb，适合大多数 X11 系统
    opts = [
        'qtInterface.py',
        '--onedir',  # 打包成一个exe
        '--windowed',  # GUI应用，不显示控制台
        # '--add-data=ffmpeg:.',
        # '--hidden-import=autocut',
         '--name=畅意快剪v2.0'# 指定生成的可执行文件的名称
        # '--icon=favicon.ico',  # 如果有图标的话
    ]
    run(opts)
