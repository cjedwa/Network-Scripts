#!/usr/bin/python

####
#### Script to parse Cisco SG300 switch configs to JSON
#### 
#### tested with python 3.5
#### Author: Cody Edwards
#### Email: cjedwa@sandia.gov 
#### Notes: need to add rest of config parameters and push into DB. possibly integrate with sgtool script. probably clean up regex too.
####

import re, sys, json
from itertools import *

## basic regex for singe line stuff
interface_regex_pattern = re.compile(r"^interface +")
hostname_regex_pattern = re.compile(r"^hostname +")
username_regex_pattern = re.compile(r"^username +")
system_mode_regex_pattern =re.compile(r"^set system mode ")
ssh_config_regex_pattern = re.compile(r"^ip ssh +")
ssh_client_config_regex_pattern = re.compile(r"^ip ssh-client +")
clock_config_regex_pattern = re.compile(r"^clock +")
sntp_config_regex_pattern = re.compile(r"^sntp +")
dns_config_regex_pattern = re.compile(r"(^ip domain +|^ip name-server)")
snmp_config_regex_pattern = re.compile(r"^snmp-server +")
web_server_config_regex_pattern = re.compile(r"(^ip http +| ip https +)")
telnet_config_regex_pattern = re.compile(r"^ip telnet server +")
## multiline regex 
keys_regex_pattern = re.compile(r"(?s)user-key(.*?)(?:(?:\r*\n){2}|exit)", re.MULTILINE)
interface_config_regex_pattern = re.compile(r"(?s)interface(.*?)(?:(?:\r*\n){2}|\!)", re.MULTILINE)

## create dict struture because I don't know how to do it dynamically
d = {}
d["interfaces"] = {}
d["users"] = {}
d["user-keys"] = {}
d["remote_access"] = {}
d["remote_access"]["ssh"] = {}
d["remote_access"]["ssh"]["ssh_server"] = []
d["remote_access"]["ssh"]["ssh_client"] = []
d["clock"] = {}
d["clock"]["config"] = []
d["clock"]["sntp"] = []
d["dns"] = []
d["snmp"] = []
d["remote_access"]["web_server"] = []
d["remote_access"]["telnet"] = []

## counter for interface number
interface_count = 0

## point me to config files. probably change this to an array of files to do multiple
cfg = open("./configs/10.0.0.1_19-03-2017.txt", 'r')

with open("./configs/10.0.0.1_19-03-2017.txt", 'r') as myfile:
    data = myfile.read()
    ## find all of the keys and add to dictionary
    rsakeys = re.findall(keys_regex_pattern, data)
    for key in rsakeys:
        key = "user-key" + key
        key = key.split("\n")
        user = key[0].split()
        d["user-keys"][user[1]] = {}
        d["user-keys"][user[1]]["key"] = key
        d["user-keys"][user[1]]["type"] = user[2]
    
    ## find all of the insterface configs and add to dictionary
    interfaces = re.findall(interface_config_regex_pattern, data)
    for interface in interfaces:
        interface = "interface" + interface
        interface = interface.split("\n")
        intnumber = interface[0].split()
        d["interfaces"][intnumber[1]] = {}
        d["interfaces"][intnumber[1]]["config"] = interface

for line in cfg:
    ## find the system mode
    if re.search(system_mode_regex_pattern, line):
        d["system_mode"] = line.rstrip('\r\n')

    ## find the system hostname
    if re.search(hostname_regex_pattern, line):
        hostname = re.split('\s+', line)
        d["hostname"] = hostname[1]

    ## get the ssh configs
    if re.search(ssh_config_regex_pattern, line):
        line = line.rstrip('\r\n')
        d["remote_access"]["ssh"]["ssh_server"].append(line)

    ## get the telnet configs
    if re.search(telnet_config_regex_pattern, line):
        line = line.rstrip('\r\n')
        d["remote_access"]["telnet"].append(line)

    ## get ssh client configs
    if re.search(ssh_client_config_regex_pattern, line):
        line = line.rstrip('\r\n')
        d["remote_access"]["ssh"]["ssh_client"].append(line)

    ## get clock configs
    if re.search(clock_config_regex_pattern, line):
        line = line.rstrip('\r\n')
        d["clock"]["config"].append(line)

    ## get sntp configs
    if re.search(sntp_config_regex_pattern, line):
        line = line.rstrip('\r\n')
        d["clock"]["sntp"].append(line)

    ## get dns configs
    if re.search(dns_config_regex_pattern, line):
        line = line.rstrip('\r\n')
        d["dns"].append(line)

    ## get snmp configs
    if re.search(snmp_config_regex_pattern, line):
        line = line.rstrip('\r\n')
        d["snmp"].append(line)

    ## get webserver configs
    if re.search(web_server_config_regex_pattern, line):
        line = line.rstrip('\r\n')
        d["remote_access"]["web_server"].append(line)

    ## find the interfaces
    if re.search(interface_regex_pattern, line):
        line = line.rstrip('\r\n')
        name = re.split('\s+', line)
        interface_count += 1
        d["interface_count"] = interface_count

    ## file the local usernames
    if re.search(username_regex_pattern, line):
        line = line.rstrip('\r\n')
        name = re.split('\s+', line)
        d["users"][name[1]] = line.rstrip('\r\n')

## remove all of the empty keys
def clean_empty(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}

clean_dict = clean_empty(d)

## pretty print in json
print(json.dumps(clean_dict, indent=4, sort_keys=True))
