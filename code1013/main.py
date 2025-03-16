# -*- coding: utf-8 -*-
# @Time    : 2024/10/13 16:12
# @Author  : zwj, lyf, lhl
# @File    : main.py
import subprocess
import time

import psutil

def check_port_in_use(port):
    """
    Check if any process is using the specified port.
    """
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
            return True
    return False




def main():
    port_to_check = 45679
    if check_port_in_use(port_to_check):
        print(f"Port {port_to_check} is in use.")
    else:
        print(f"Port {port_to_check} is not in use.")
        # 启动 app.py 进程
        app_process = subprocess.Popen(['python', 'autocut/service/app.py'])

    # 启动 qtInterface.py 进程
    qt_process = subprocess.Popen(['python', 'qtInterface.py'])

    try:
        # 等待 qtInterface.py 进程结束
        while qt_process.poll() is None:
            time.sleep(1)  # 可以根据需要调整检查的频率

    finally:
        # 当 qtInterface.py 进程结束时，终止 app.py 进程
        if app_process.poll() is None:
            app_process.terminate()
    # app_process.terminate()
    # app_process.communicate()


if __name__ == "__main__":
    main()

# sudo lsof -i :45679
