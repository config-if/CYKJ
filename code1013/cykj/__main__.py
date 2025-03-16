# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:23
# @Author  : zwj, lyf, lhl
# @File    : __main__.py.py
from main import main
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

if __name__ == "__main__":
    main()
