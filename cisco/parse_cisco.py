#!/usr/bin/python

####
#### Script to parse Cisco SG300 switch configs to JSON
#### 
#### tested with python 3.5
#### Author: Cody Edwards
#### Email: cjedwa@sandia.gov 
#### Notes: need to add rest of config parameters and push into DB. possibly integrate with sgtool script. probably clean up regex too.
####

import re, sys, json, argparse

arguments = argparse.ArgumentParser(description='Tool to parse Cisco SG300 switch configs to json')
arguments.add_argument("--xfile", '-f', nargs='?', help='Parse one file. Takes one arg.')
#filegrp.add_argument('--directory', '-d', nargs='?', help='Parse all files in directory. Takes one arg.')
args = arguments.parse_args()

## basic regex for singe line stuff
interface_regex_pattern = re.compile(r"^interface +")
hostname_regex_pattern = re.compile(r"^hostname +")
username_regex_pattern = re.compile(r"^username +")
system_mode_regex_pattern =re.compile(r"^set system mode ")
ssh_config_regex_pattern = re.compile(r"^ip ssh +")
ssh_client_config_regex_pattern = re.compile(r"^ip ssh-client +")
clock_config_regex_pattern = re.compile(r"^clock +")
sntp_config_regex_pattern = re.compile(r"(^sntp +|^encrypted sntp +)")
dns_config_regex_pattern = re.compile(r"(^ip domain +|^ip name-server)")
snmp_config_regex_pattern = re.compile(r"^snmp-server +")
web_server_config_regex_pattern = re.compile(r"(^ip http +| ip https +)")
telnet_config_regex_pattern = re.compile(r"^ip telnet server +")
dhcp_config_regex_pattern = re.compile(r"(^ip dhcp +|^ip helper +)")
bonjour_config_regex_pattern = re.compile(r"^bonjour +")
aaa_config_regex_pattern = re.compile(r"^aaa +")
passwords_config_regex_pattern = re.compile(r"^passwords +")
logging_config_regex_pattern = re.compile(r"^logging +")
dot1x_config_regex_pattern = re.compile(r"^dot1x +")
cdp_config_regex_pattern = re.compile(r"^cdp +")
lldp_config_regex_pattern = re.compile(r"^lldp +")
radius_config_regex_pattern = re.compile(r"(^radius-server +|encrypted radius-server +)")
tacacs_config_regex_pattern = re.compile(r"^tacacs-server +")
crypto_config_regex_pattern = re.compile(r"^crypto +")
default_gateway_config_regex_pattern = re.compile(r"^ip default-gateway +")
##START NOT DONE
enable_config_regex_pattern = re.compile(r"^enable +")
rmon_config_regex_pattern = re.compile(r"^rmon +")
eee_config_regex_pattern = re.compile(r"^eee +")
green_ethernet_config_regex_pattern = re.compile(r"^green-ethernet +")
port_channel_config_regex_pattern = re.compile(r"(^port-channel +|^Port-Channel +)")
bridge_config_regex_pattern = re.compile(r"^bridge +")
spanning_tree_config_regex_pattern = re.compile(r"^spanning-tree +")
jumbo_frame_config_regex_pattern = re.compile(r"^port jumbo-frame")
voice_vlan_config_regex_pattern = re.compile(r"^voice vlan +")
ssd_config_regex_pattern = re.compile(r"(^ssd +|^no ssd +|^ssd-control-*|file SSD +)")
igmp_config_regex_pattern = re.compile(r"^ip igmp +")
ipv6_config_regex_pattern = re.compile(r"^ipv6 +")
lacp_config_regex_pattern = re.compile(r"^lacp +")
gvrp_config_regex_pattern = re.compile(r"^gvrp +")
source_guard_config_regex_pattern = re.compile(r"^ip source-guard +")
arp_config_regex_pattern = re.compile(r"(^ip arp +|^arp +)")
tunnel_config_regex_pattern = re.compile(r"(^tunnel +|^Tunnel +)")
route_config_regex_pattern = re.compile(r"^ip route +")
service_config_regex_pattern = re.compile(r"^service +")
qos_config_regex_pattern = re.compile(r"(^qos +|^class-map +|^policy-map +)")
security_suite_config_regex_pattern = re.compile(r"^security-suite +")
system_router_config_regex_pattern = re.compile(r"^system router +")
udld_config_regex_pattern = re.compile(r"^udld +")

#END
## multiline regex 
keys_regex_pattern = re.compile(r"(?s)^user-key(.*?)(?:(?:\r*\n){2}|exit)", re.MULTILINE)
interface_config_regex_pattern = re.compile(r"(?s)^interface(.*?)(?:(?:\r*\n){2}|\!)", re.MULTILINE)
banner_config_regex_pattern = re.compile(r"(?s)^banner(.*?)(?:(?:\r*\n){2}|^\^C)", re.MULTILINE)
ssh_line_config_regex_pattern = re.compile(r"(?s)^line ssh(.*?)(?:(?:\r*\n){2}|^exit)", re.MULTILINE)
console_line_config_regex_pattern = re.compile(r"(?s)^line console(.*?)(?:(?:\r*\n){2}|^exit)", re.MULTILINE)
vlan_config_regex_pattern = re.compile(r"(?s)^vlan database(.*?)(?:(?:\r*\n){2}|^exit)", re.MULTILINE)

## create dict struture because I don't know how to do it dynamically
d = {}
d["interfaces"] = {}
d["users"] = {}
d["discovery"] = {}
d["discovery"]["cdp"] = []
d["discovery"]["lldp"] = []
d["user-keys"] = {}
d["remote_access"] = {}
d["remote_access"]["ssh"] = {}
d["remote_access"]["ssh"]["ssh_server"] = []
d["remote_access"]["ssh"]["ssh_client"] = []
d["time"] = {}
d["banner"] = {}
d["line"] = {}
d["vlans"] = {}
d["vlans"]["voice"] = []
d["vlans"]["standard"] = []
d["crypto"] = []
d["time"]["clock"] = []
d["time"]["sntp"] = []
d["network"] = []
d["dns"] = []
d["hardware"] = {}
d["hardware"]["disk"] = []
d["snmp"] = []
d["remote_access"]["web_server"] = []
d["remote_access"]["telnet"] = []
d["dhcp"] = []
d["aaa"] = []
d["passwords"] = []
d["logging"] = []
d["dot1x"] = []
d["auth"] = {}
d["auth"]["tacacs"] = []
d["auth"]["radius"] = []
d["bonjour"] = []
d["no_match"] = []

## counter for interface number
interface_count = 0

## point me to config files. probably change this to an array of files to do multiple
if args.xfile:
    cfg = open(args.xfile, 'r')
    
#cfg = open("./configs/192.168.200.32_13-03-2017.txt", 'r')

with open(args.xfile, 'r') as myfile:
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
    data = re.sub(keys_regex_pattern, r'', data) 

    ## find all of the insterface configs and add to dictionary
    interfaces = re.findall(interface_config_regex_pattern, data)
    for interface in interfaces:
        interface = "interface" + interface
        interface = interface.split("\n")
        intnumber = interface[0].split()
        d["interfaces"][intnumber[1]] = []
        d["interfaces"][intnumber[1]].append(interface)
    data = re.sub(interface_config_regex_pattern, r'', data) 

    ## find banners in configs and add to dictionary
    banners = re.findall(banner_config_regex_pattern, data)
    for banner in banners:
        banner = "banner" + banner + "^C"
        banner = banner.split("\n")
        banner_top = banner[0].split()
        d["banner"]["config"] = banner
    data = re.sub(banner_config_regex_pattern, r'', data) 

    ## find line ssh in configs and add to dictionary
    line_ssh = re.findall(ssh_line_config_regex_pattern, data)
    line_ssh = "line ssh" + line_ssh[0]
    line_ssh = line_ssh.split("\n")
    line_top = line_ssh[0].split()
    d["line"][line_top[1]] = []
    d["line"][line_top[1]] = line_ssh
    data = re.sub(ssh_line_config_regex_pattern, r'', data) 

    ## find line console in configs and add to dictionary
    line_console = re.findall(console_line_config_regex_pattern, data)
    line_console = "line console" + line_console[0]
    line_console = line_console.split("\n")
    line_top = line_console[0].split()
    d["line"][line_top[1]] = []
    d["line"][line_top[1]] = line_console
    data = re.sub(console_line_config_regex_pattern, r'', data) 

    ## Track down VLANs
    vlans = re.findall(vlan_config_regex_pattern, data)
    vlans = "vlan database" + vlans[0]
    vlans = vlans.split('\n')
    vlans = re.sub(r"vlan", r'', vlans[1]).split(',')
    d["vlans"]["standard"] = vlans
    data = re.sub(ssh_line_config_regex_pattern, r'', data) 

    for line in data.split('\n'):
        ## find the system mode
        if re.search(system_mode_regex_pattern, line):
            d["system_mode"] = line.rstrip('\r\n')
            line = "__MATCHED__" + line
    
        ## find the system hostname
        if re.search(hostname_regex_pattern, line):
            hostname = re.split('\s+', line)
            d["hostname"] = hostname[1]
            line = "__MATCHED__" + line
    
        ## get the ssh configs
        if re.search(ssh_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["remote_access"]["ssh"]["ssh_server"].append(line)
            line = "__MATCHED__" + line
    
        ## get the telnet configs
        if re.search(telnet_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["remote_access"]["telnet"].append(line)
            line = "__MATCHED__" + line
    
        ## get ssh client configs
        if re.search(ssh_client_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["remote_access"]["ssh"]["ssh_client"].append(line)
            line = "__MATCHED__" + line
    
        ## get clock configs
        if re.search(clock_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["time"]["clock"].append(line)
            line = "__MATCHED__" + line
    
        ## get sntp configs
        if re.search(sntp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["time"]["sntp"].append(line)
            line = "__MATCHED__" + line
    
        ## get dns configs
        if re.search(dns_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["dns"].append(line)
            line = "__MATCHED__" + line

        ## get dns configs
        if re.search(default_gateway_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["network"].append(line)
            line = "__MATCHED__" + line

        ## get ssd configs
        if re.search(ssd_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["hardware"]["disk"].append(line)
            line = "__MATCHED__" + line

        ## get logging configs
        if re.search(logging_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["logging"].append(line)
            line = "__MATCHED__" + line
        ## get dot1x configs
        if re.search(dot1x_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["dot1x"].append(line)
            line = "__MATCHED__" + line
        ## get dhcp configs
        if re.search(dhcp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["dhcp"].append(line)
            line = "__MATCHED__" + line
        ## get passwords configs
        if re.search(passwords_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["passwords"].append(line)
            line = "__MATCHED__" + line
        ## get aaa configs
        if re.search(aaa_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["aaa"].append(line)
            line = "__MATCHED__" + line
        ## get bonjour configs
        if re.search(bonjour_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["bonjour"].append(line)
            line = "__MATCHED__" + line
    
        ## get lldp configs
        if re.search(lldp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["discovery"]["lldp"].append(line)
            line = "__MATCHED__" + line
    
        ## get cdp configs
        if re.search(cdp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["discovery"]["cdp"].append(line)
            line = "__MATCHED__" + line
    
        ## get radius configs
        if re.search(radius_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["auth"]["radius"].append(line)
            line = "__MATCHED__" + line
    
        ## get tacacs configs
        if re.search(tacacs_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["auth"]["tacacs"].append(line)
            line = "__MATCHED__" + line
        ## get crypto configs
        if re.search(crypto_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["crypto"].append(line)
            line = "__MATCHED__" + line
    
        ## get snmp configs
        if re.search(snmp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["snmp"].append(line)
            line = "__MATCHED__" + line
        ## get webserver configs
        if re.search(web_server_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["remote_access"]["web_server"].append(line)
            line = "__MATCHED__" + line
    
        ## get voice vlan configs
        if re.search(voice_vlan_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["vlans"]["voice"].append(line)
            line = "__MATCHED__" + line
    
        ## find the interfaces
        if re.search(interface_regex_pattern, line):
            line = line.rstrip('\r\n')
            name = re.split('\s+', line)
            interface_count += 1
            d["interface_count"] = interface_count
        ## get rid of junk 
        if re.search(r'(^\!|^\@|^exit|^CLI|^vlan +|^v1.4+|^config-file-header)', line):
            line = line.rstrip('\r\n')
            line = "__MATCHED__" + line
    
        ## file the local usernames
        if re.search(username_regex_pattern, line):
            line = line.rstrip('\r\n')
            name = re.split('\s+', line)
            d["users"][name[1]] = line.rstrip('\r\n')
            line = "__MATCHED__" + line
        else:
            matched = re.search(r"^__MATCHED__*", line)
            if not matched:
                d["no_match"].append(line)
        #print(d)
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
