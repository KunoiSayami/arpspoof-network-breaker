# -*- coding: utf-8 -*-
# main.py
# Copyright (C) 2019 KunoiSayami
#
# This module is part of arpspoof-network-breaker and is released under
# the AGPL v3 License: https://www.gnu.org/licenses/agpl-3.0.txt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import subprocess
import time
from typing import List
import signal

def runable(cmd: list, sleep_time: int or float, wait: bool = False, exit_msg: str = ''):
	sub = subprocess.Popen(cmd)
	time.sleep(sleep_time)
	sub.send_signal(signal.SIGINT)
	if exit_msg != '': print('{}: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), exit_msg))
	if wait: sub.wait()
