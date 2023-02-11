#!/usr/bin/python3

from helpers import init_log
from data_collection import collect_data

import os

pidFile = open("main.pid", "w")
pidFile.write(str(os.getpid()))
pidFile.close()

if __name__ == '__main__':
    init_log()
    collect_data()
