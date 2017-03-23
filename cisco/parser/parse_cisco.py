#!/usr/bin/python

####
#### Script to parse Cisco SG300 switch configs to JSON
#### 
#### tested with python 3.5
#### Author: Cody Edwards
#### Email: cjedwa@sandia.gov 
#### Notes: need to add rest of config parameters and push into DB. possibly integrate with sgtool script. probably clean up regex too. Also finish adding the NOT DONE items below.
####

import re, sys, json, argparse, os, datetime, time
from cisco_regex import *
#arguments = argparse.ArgumentParser(description='Tool to parse Cisco SG300 switch configs to json')
#arguments.add_argument("--xfile", '-f', nargs='?', help='Parse one file. Takes one arg.')
#args = arguments.parse_args()


def parser(): 
   #arguments = argparse.ArgumentParser(description='Tool to parse Cisco SG300 switch configs to json')
   #arguments.add_argument("--xfile", '-f', nargs='?', help='Parse one file. Takes one arg.')
   #args = arguments.parse_args()
   path = '/home/cjedwa/cisco_configs/'
   grabfiles = os.listdir(path)
   config_files = []
   result = []
   for config in grabfiles:
       config_files.append(path + config)
   now = datetime.datetime.now()    
   #epoch = int(now.strftime("%s")) * 1000
   ## create dict struture because I don't know how to do it dynamically
   d = {}
   d["auth"] = {}
   d["auth"]["aaa"] = []
   d["auth"]["radius"] = []
   d["auth"]["tacacs"] = []
   d["banner"] = {}
   d["bonjour"] = []
   d["crypto"] = []
   d["dhcp"] = []
   d["discovery"] = {}
   d["discovery"]["cdp"] = []
   d["discovery"]["lldp"] = []
   d["dns"] = []
   d["dot1x"] = []
   d["hardware"] = {}
   d["hardware"]["disk"] = []
   d["hardware"]["power"] = []
   d["interfaces"] = {}
   d["line"] = {}
   d["management"] = {}
   d["management"]["logging"] = []
   d["management"]["snmp"] = []
   d["network"] = []
   d["no_match"] = []
   d["passwords"] = []
   d["remote_access"] = {}
   d["remote_access"]["ssh"] = {}
   d["remote_access"]["ssh"]["ssh_client"] = []
   d["remote_access"]["ssh"]["ssh_server"] = []
   d["remote_access"]["telnet"] = []
   d["remote_access"]["web_server"] = []
   d["time"] = {}
   d["time"]["clock"] = []
   d["time"]["sntp"] = []
   d["users"] = {}
   d["users"]["chain"] = []
   d["vlans"] = {}
   d["vlans"]["standard"] = []
   d["vlans"]["voice"] = []
   d["sshkeys"] = {}
   d["raw_config"] = {}
   d["raw_config"]["conf"] = []
   d["created_at"] = now.strftime("%Y-%m-%d %H:%M")
   ## counter for interface number
   for config in config_files:
       interface_count = 0
        
       ## point me to config files. probably change this to an array of files to do multiple
       #if self.args.xfile:
       #    cfg = open(self.args.xfile, 'r')
           
       #cfg = open("./configs/192.168.200.32_13-03-2017.txt", 'r')
       
       with open(config, 'r') as myfile:
           data = myfile.read()
           ## find all of the keys and add to dictionary
           rsakeys = re.findall(keys_regex_pattern, data)
           for key in rsakeys:
               key = "user-key" + key
               key = key.split("\n")
               user = key[0].split()
               uname = user[1]
               d["sshkeys"][uname] = []
               d["sshkeys"][uname] = key
               for i in key:
                   d["raw_config"]["conf"].append(i)
           data = re.sub(keys_regex_pattern, r'', data) 
       
           ## find all of the insterface configs and add to dictionary
           interfaces = re.findall(interface_config_regex_pattern, data)
           for interface in interfaces:
               interface = "interface" + interface
               interface = interface.split("\n")
               intnumber = interface[0].split()
               d["interfaces"][intnumber[1]] = []
               d["interfaces"][intnumber[1]] = interface
               for i in interface:
                   d["raw_config"]["conf"].append(i)
           data = re.sub(interface_config_regex_pattern, r'', data) 
       
           ## find banners in configs and add to dictionary
           banners = re.findall(banner_config_regex_pattern, data)
           for banner in banners:
               banner = "banner" + banner + "^C"
               banner = banner.split("\n")
               banner_top = banner[0].split()
               d["banner"] = banner
               for i in banner:
                   d["raw_config"]["conf"].append(i)
           data = re.sub(banner_config_regex_pattern, r'', data) 
       
           ## find line ssh in configs and add to dictionary
           if re.findall(ssh_line_config_regex_pattern, data):
               line_ssh = re.findall(ssh_line_config_regex_pattern, data)
               line_ssh = "line ssh" + line_ssh[0]
               line_ssh = line_ssh.split("\n")
               line_top = line_ssh[0].split()
               d["line"][line_top[1]] = []
               d["line"][line_top[1]] = line_ssh
               for i in line_ssh:
                   d["raw_config"]["conf"].append(i)
               data = re.sub(ssh_line_config_regex_pattern, r'', data) 
       
           ## find line console in configs and add to dictionary
           elif re.findall(console_line_config_regex_pattern, data):
               line_console = re.findall(console_line_config_regex_pattern, data)
               line_console = re.findall(console_line_config_regex_pattern, data)
               line_console = "line console" + line_console[0]
               line_console = line_console.split("\n")
               line_top = line_console[0].split()
               d["line"][line_top[1]] = []
               d["line"][line_top[1]] = line_console
               d["raw_config"]["conf"].append(line_console)
               data = re.sub(console_line_config_regex_pattern, r'', data) 
       
           ## Track down VLANs
           elif re.findall(vlan_config_regex_pattern, data):
               vlans = re.findall(vlan_config_regex_pattern, data)
               vlans = "vlan database" + vlans[0]
               vlans = vlans.split('\n')
               d["raw_config"]["conf"].append(vlans)
               vlans = re.sub(r"vlan", r'', vlans[1]).split(',')
               d["vlans"]["standard"] = vlans
               data = re.sub(ssh_line_config_regex_pattern, r'', data) 
       
           for line in data.split('\n'):
               ## find the system mode
               if re.search(system_mode_regex_pattern, line):
                   d["system_mode"] = line.rstrip('\r\n')
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## find the system hostname
               elif re.search(hostname_regex_pattern, line):
                   hostname = line.rstrip('\r\n')
                   d["hostname"] = hostname
                   d["raw_config"]["conf"].append(hostname)
                   h = hostname.split()
                   print(h)
                   d['_id'] = h[1]
                   line = "__MATCHED__" + line
           
               ## get the ssh configs
               elif re.search(ssh_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["remote_access"]["ssh"]["ssh_server"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get the telnet configs
               elif re.search(telnet_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["remote_access"]["telnet"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get ssh client configs
               elif re.search(ssh_client_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["raw_config"]["conf"].append(line)
                   d["remote_access"]["ssh"]["ssh_client"].append(line)
                   line = "__MATCHED__" + line
           
               ## get clock configs
               elif re.search(clock_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["time"]["clock"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get sntp configs
               elif re.search(sntp_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["time"]["sntp"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get dns configs
               elif re.search(dns_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["dns"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
       
               ## get dns configs
               elif re.search(default_gateway_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["network"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
       
               ## get ssd configs
               elif re.search(ssd_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["hardware"]["disk"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
       
               ## get logging configs
               elif re.search(logging_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["management"]["logging"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
               ## get dot1x configs
               elif re.search(dot1x_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["dot1x"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
               ## get dhcp configs
               elif re.search(dhcp_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["dhcp"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
               ## get passwords configs
               elif re.search(passwords_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["raw_config"]["conf"].append(line)
                   d["passwords"].append(line)
                   line = "__MATCHED__" + line
               ## get aaa configs
               elif re.search(aaa_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["raw_config"]["conf"].append(line)
                   d["auth"]["aaa"].append(line)
                   line = "__MATCHED__" + line
               ## get bonjour configs
               elif re.search(bonjour_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["bonjour"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get lldp configs
               elif re.search(lldp_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["discovery"]["lldp"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get cdp configs
               elif re.search(cdp_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["discovery"]["cdp"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get radius configs
               elif re.search(radius_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["auth"]["radius"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get tacacs configs
               elif re.search(tacacs_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["auth"]["tacacs"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
               ## get crypto configs
               elif re.search(crypto_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["users"]["chain"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get arp configs
               elif re.search(arp_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["network"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
               ## get snmp configs
               elif re.search(snmp_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["management"]["snmp"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
               ## get webserver configs
               elif re.search(web_server_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["remote_access"]["web_server"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get eee configs
               elif re.search(eee_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["hardware"]["power"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get green eth configs
               elif re.search(green_ethernet_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["hardware"]["power"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## get voice vlan configs
               elif re.search(voice_vlan_config_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   d["vlans"]["voice"].append(line)
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
           
               ## find the interfaces
               elif re.search(interface_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   name = re.split('\s+', line)
                   interface_count += 1
                   d["interface_count"] = interface_count
               ## get rid of junk 
               elif re.search(r'(^\!|^\@|^exit|^CLI|^vlan +|^v1.4+|^config-file-header)', line):
                   line = line.rstrip('\r\n')
                   line = "__MATCHED__" + line
           
               ## file the local usernames
               elif re.search(username_regex_pattern, line):
                   line = line.rstrip('\r\n')
                   name = re.split('\s+', line)
                   d["users"][name[1]] = {}
                   d["users"][name[1]]["local-account"] = line.rstrip('\r\n')
                   d["raw_config"]["conf"].append(line)
                   line = "__MATCHED__" + line
               else:
                   matched = re.search(r"^__MATCHED__*", line)
                   if not matched:
                       d["no_match"].append(line)
                       d["raw_config"]["conf"].append(line)
               #print(d)
       ## remove all of the empty keys
       def clean_empty(d):
           if not isinstance(d, (dict, list)):
               return d
           if isinstance(d, list):
               return [v for v in (clean_empty(v) for v in d) if v]
           return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}
       
       result.append(clean_empty(d))
       result.append(d["_id"])
       #print(json.dumps(clean_dict, indent=4, sort_keys=True))
       return result
       
       ## pretty print in json
      # print(json.dumps(clean_dict, indent=4, sort_keys=True))
