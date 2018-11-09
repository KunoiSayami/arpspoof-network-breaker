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