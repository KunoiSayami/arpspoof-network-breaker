# ARPSPOOF NETWORK BREAKER

Using arp spoofing technology to cut off the network of the specified computer.

## WARNING & DISCLAIMER

**Use of this program may violate local laws and all consequences of using the Program are not related to this project.**

If the code of the project is used (including but not limited to its derivative products), which means you fully understand this warning and disclaimer, you are fully responsible for the consequences of using this project (including but not limited to its derivative products).

The project owner has the final interpretation of this disclaimer.

## Operating Environment
Python 3.4 and above is required

The following libraries are required:

* netifaces

The following executable files are required:

* netdiscover
* arpspoof

*Tested successfully on [Kali Linux](https://www.kali.org/downloads/)*

## Run

* Copy `config.ini.default` to `config.ini`.
* Input target MAC address or IP address to `config.ini`, then run it with `python3 main.py`.

or:

* Just run `python3 main.py <MAC address or IP address>`

**Make sure you are in the same subnet.**

## License

[![](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.txt)

Copyright (C) 2018 Too-Naive

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.