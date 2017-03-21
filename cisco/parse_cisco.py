#!/usr/bin/python

####
#### Script to parse Cisco SG300 switch configs to JSON
#### 
#### tested with python 3.5
#### Author: Cody Edwards
#### Email: cjedwa@sandia.gov 
#### Notes: need to add rest of config parameters and push into DB. possibly integrate with sgtool script. probably clean up regex too. Also finish adding the NOT DONE items below.
####

import re, sys, json, argparse

arguments = argparse.ArgumentParser(description='Tool to parse Cisco SG300 switch configs to json')
arguments.add_argument("--xfile", '-f', nargs='?', help='Parse one file. Takes one arg.')
#filegrp.add_argument('--directory', '-d', nargs='?', help='Parse all files in directory. Takes one arg.')
args = arguments.parse_args()

## basic regex for singe line stuff
aaa_config_regex_pattern = re.compile(r"^aaa +")
bonjour_config_regex_pattern = re.compile(r"^bonjour +")
cdp_config_regex_pattern = re.compile(r"^cdp +")
clock_config_regex_pattern = re.compile(r"^clock +")
crypto_config_regex_pattern = re.compile(r"^crypto +")
default_gateway_config_regex_pattern = re.compile(r"^ip default-gateway +")
dhcp_config_regex_pattern = re.compile(r"(^ip dhcp +|^ip helper +)")
dns_config_regex_pattern = re.compile(r"(^ip domain +|^ip name-server)")
dot1x_config_regex_pattern = re.compile(r"^dot1x +")
hostname_regex_pattern = re.compile(r"^hostname +")
interface_regex_pattern = re.compile(r"^interface +")
lldp_config_regex_pattern = re.compile(r"^lldp +")
logging_config_regex_pattern = re.compile(r"^logging +")
passwords_config_regex_pattern = re.compile(r"^passwords +")
radius_config_regex_pattern = re.compile(r"(^radius-server +|encrypted radius-server +)")
snmp_config_regex_pattern = re.compile(r"^snmp-server +")
sntp_config_regex_pattern = re.compile(r"(^sntp +|^encrypted sntp +)")
ssh_client_config_regex_pattern = re.compile(r"^ip ssh-client +")
ssh_config_regex_pattern = re.compile(r"^ip ssh +")
system_mode_regex_pattern =re.compile(r"^set system mode ")
tacacs_config_regex_pattern = re.compile(r"^tacacs-server +")
telnet_config_regex_pattern = re.compile(r"^ip telnet server +")
username_regex_pattern = re.compile(r"^username +")
web_server_config_regex_pattern = re.compile(r"(^ip http +| ip https +)")
ssd_config_regex_pattern = re.compile(r"(^ssd +|^no ssd +|^ssd-control-*|file SSD +)")
voice_vlan_config_regex_pattern = re.compile(r"^voice vlan +")
eee_config_regex_pattern = re.compile(r"^eee +")
green_ethernet_config_regex_pattern = re.compile(r"^green-ethernet +")
##START NOT DONE
arp_config_regex_pattern = re.compile(r"(^ip arp +|^arp +)")
bridge_config_regex_pattern = re.compile(r"^bridge +")
enable_config_regex_pattern = re.compile(r"^enable +")
gvrp_config_regex_pattern = re.compile(r"^gvrp +")
igmp_config_regex_pattern = re.compile(r"^ip igmp +")
ipv6_config_regex_pattern = re.compile(r"^ipv6 +")
jumbo_frame_config_regex_pattern = re.compile(r"^port jumbo-frame")
lacp_config_regex_pattern = re.compile(r"^lacp +")
port_channel_config_regex_pattern = re.compile(r"(^port-channel +|^Port-Channel +)")
qos_config_regex_pattern = re.compile(r"(^qos +|^class-map +|^policy-map +)")
rmon_config_regex_pattern = re.compile(r"^rmon +")
route_config_regex_pattern = re.compile(r"^ip route +")
security_suite_config_regex_pattern = re.compile(r"^security-suite +")
service_config_regex_pattern = re.compile(r"^service +")
source_guard_config_regex_pattern = re.compile(r"^ip source-guard +")
spanning_tree_config_regex_pattern = re.compile(r"^spanning-tree +")
system_router_config_regex_pattern = re.compile(r"^system router +")
tunnel_config_regex_pattern = re.compile(r"(^tunnel +|^Tunnel +)")
udld_config_regex_pattern = re.compile(r"^udld +")
#END
## multiline regex 
banner_config_regex_pattern = re.compile(r"(?s)^banner(.*?)(?:(?:\r*\n){2}|^\^C)", re.MULTILINE)
console_line_config_regex_pattern = re.compile(r"(?s)^line console(.*?)(?:(?:\r*\n){2}|^exit)", re.MULTILINE)
interface_config_regex_pattern = re.compile(r"(?s)^interface(.*?)(?:(?:\r*\n){2}|\!)", re.MULTILINE)
keys_regex_pattern = re.compile(r"(?s)^user-key(.*?)(?:(?:\r*\n){2}|exit)", re.MULTILINE)
ssh_line_config_regex_pattern = re.compile(r"(?s)^line ssh(.*?)(?:(?:\r*\n){2}|^exit)", re.MULTILINE)
vlan_config_regex_pattern = re.compile(r"(?s)^vlan database(.*?)(?:(?:\r*\n){2}|^exit)", re.MULTILINE)

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
#d["user-keys"] = {}
d["users"] = {}
d["users"]["chain"] = []
d["vlans"] = {}
d["vlans"]["standard"] = []
d["vlans"]["voice"] = []

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
        print(key)
        user = key[0].split()
        d["users"][user[1]] = {}
        d["users"][user[1]]["key"] = [] 
        d["users"][user[1]]["key"].append(key)
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
        d["banner"] = banner
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
        elif re.search(hostname_regex_pattern, line):
            hostname = line.rstrip('\r\n')
            d["hostname"] = hostname
            line = "__MATCHED__" + line
    
        ## get the ssh configs
        elif re.search(ssh_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["remote_access"]["ssh"]["ssh_server"].append(line)
            line = "__MATCHED__" + line
    
        ## get the telnet configs
        elif re.search(telnet_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["remote_access"]["telnet"].append(line)
            line = "__MATCHED__" + line
    
        ## get ssh client configs
        elif re.search(ssh_client_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["remote_access"]["ssh"]["ssh_client"].append(line)
            line = "__MATCHED__" + line
    
        ## get clock configs
        elif re.search(clock_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["time"]["clock"].append(line)
            line = "__MATCHED__" + line
    
        ## get sntp configs
        elif re.search(sntp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["time"]["sntp"].append(line)
            line = "__MATCHED__" + line
    
        ## get dns configs
        elif re.search(dns_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["dns"].append(line)
            line = "__MATCHED__" + line

        ## get dns configs
        elif re.search(default_gateway_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["network"].append(line)
            line = "__MATCHED__" + line

        ## get ssd configs
        elif re.search(ssd_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["hardware"]["disk"].append(line)
            line = "__MATCHED__" + line

        ## get logging configs
        elif re.search(logging_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["management"]["logging"].append(line)
            line = "__MATCHED__" + line
        ## get dot1x configs
        elif re.search(dot1x_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["dot1x"].append(line)
            line = "__MATCHED__" + line
        ## get dhcp configs
        elif re.search(dhcp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["dhcp"].append(line)
            line = "__MATCHED__" + line
        ## get passwords configs
        elif re.search(passwords_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["passwords"].append(line)
            line = "__MATCHED__" + line
        ## get aaa configs
        elif re.search(aaa_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["auth"]["aaa"].append(line)
            line = "__MATCHED__" + line
        ## get bonjour configs
        elif re.search(bonjour_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["bonjour"].append(line)
            line = "__MATCHED__" + line
    
        ## get lldp configs
        elif re.search(lldp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["discovery"]["lldp"].append(line)
            line = "__MATCHED__" + line
    
        ## get cdp configs
        elif re.search(cdp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["discovery"]["cdp"].append(line)
            line = "__MATCHED__" + line
    
        ## get radius configs
        elif re.search(radius_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["auth"]["radius"].append(line)
            line = "__MATCHED__" + line
    
        ## get tacacs configs
        elif re.search(tacacs_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["auth"]["tacacs"].append(line)
            line = "__MATCHED__" + line
        ## get crypto configs
        elif re.search(crypto_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["users"]["chain"].append(line)
            line = "__MATCHED__" + line
    
        ## get arp configs
        elif re.search(arp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["network"].append(line)
            line = "__MATCHED__" + line
        ## get snmp configs
        elif re.search(snmp_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["management"]["snmp"].append(line)
            line = "__MATCHED__" + line
        ## get webserver configs
        elif re.search(web_server_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["remote_access"]["web_server"].append(line)
            line = "__MATCHED__" + line
    
        ## get eee configs
        elif re.search(eee_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["hardware"]["power"].append(line)
            line = "__MATCHED__" + line
    
        ## get green eth configs
        elif re.search(green_ethernet_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["hardware"]["power"].append(line)
            line = "__MATCHED__" + line
    
        ## get voice vlan configs
        elif re.search(voice_vlan_config_regex_pattern, line):
            line = line.rstrip('\r\n')
            d["vlans"]["voice"].append(line)
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
