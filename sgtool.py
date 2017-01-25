#!/usr/bin/env python
from __future__ import print_function
import sys, argparse, datetime, getpass, yaml, re, json, os, time, pwd
from netmiko import ConnectHandler
from netmiko.cisco import CiscoS300SSH
from netaddr import *

def parseArgs():
    parser = argparse.ArgumentParser(description='sgtool: Program to configure simplify configuration of Cisco SG300 Switches.\nAuthor: Cody Edwards\n cjedwa@sandia.gov')

    authgroup = parser.add_mutually_exclusive_group()
    authgroup.add_argument('--password', '-P', action='store_true', help='Prompt for SSH password.')
    authgroup.add_argument('--usekeys', '-k', action='store', help='Use SSH keys. Requires Keyfile arg if not in standard spot.' )

    commandgroup = parser.add_mutually_exclusive_group()
    commandgroup.add_argument('--command', '-c', help='Runs a single command from user mode')
    commandgroup.add_argument('--cmdfile', '-f', help='Reads multiple commands from <file> separated by newline and runs in configuration mode')
    commandgroup.add_argument('--test', '-t', action='store_true' ,help='Connect to test, no commands.')
    commandgroup.add_argument('--addvlan', '-a', help='Add vlans to device. Takes comma separated list. EX. -a "1, 2, 3" would add vlans 1, 2, and 3.')
    commandgroup.add_argument('--remvlan', '-r', help='Remove vlans from device. Takes comma separated list. EX. -r "1, 2, 3" would remove vlans 1, 2, and 3.')
    commandgroup.add_argument('--storeconf', '-s', nargs='?', help='Backup device config. Argument is directory to place config')

    hostgroup = parser.add_mutually_exclusive_group()
    hostgroup.add_argument("--host", '-H', help='Interact with a single host. Takes an IP addr or resolvable name.')
    hostgroup.add_argument("--nodefile", '-n', nargs='?', help='Reads multiple nodes separated by newline from <file>. Assumes same password for all devices if used with -P')
    hostgroup.add_argument('--yaml', '-y', nargs='?', help='Import node settings from yaml file.')

    parser.add_argument('-u', default=pwd.getpwuid(os.getuid()).pw_name, help='User name for session.')
    parser.add_argument('--each', '-e', action='store_true', help='Pause for input between multiple SSH sessions.')
    parser.add_argument('--verbose', '-V', action='store_true', help='Toggle verbosity')
    parser.add_argument('--port', '-p', default='22', help='Specify port for SSH conn. Defaults to 22')
    args = parser.parse_args() 
    return args

def devList(args):
    uid = pwd.getpwuid(os.getuid()).pw_name
    
    addr_list = []
    password = ''

    if args.u:
        uname = args.u

    if args.nodefile:
        with open(args.nodefile) as f:
            temp = f.readlines()
            node_list = map(lambda temp: temp.strip(), temp)
            if args.usekeys:
                for i in node_list:
                    addr_list.append( 
                        {
                        'device_type': 'cisco_s300',
                        'ip':   i,
                        'username': str(uname),
                        'password': str(password),
                        'port' : args.port,        
                        'verbose': args.verbose,
                        'use_keys': True,
                        'key_file': args.usekeys
                        }
                    )
            elif args.password:
                if not password:
                    password = getpass.getpass(prompt="Enter Password: ")
                for i in node_list:
                    addr_list.append( 
                        {
                        'device_type': 'cisco_s300',
                        'ip':   i,
                        'username': str(uname),
                        'password': str(password),
                        'port' : args.port,        
                        'verbose': args.verbose,
                        'use_keys': False,
                        }
                    )

    if args.host:
        if args.usekeys:
            addr_list.append( 
                {
                'device_type': 'cisco_s300',
                'ip': args.host,
                'username': str(uname),
                'password': str(password),
                'port' : args.port,        
                'verbose': args.verbose,
                'use_keys': True,
                'key_file': args.usekeys
                }
            )
        elif args.password:
            password = getpass.getpass(prompt="Enter Password: ")
            addr_list.append( 
                {
                'device_type': 'cisco_s300',
                'ip': args.host,
                'username': str(uname),
                'password': str(password),
                'port' : args.port,        
                'verbose': args.verbose,
                'use_keys': False,
                }
            )
        else:
            print(" ERROR: Must use either keys(-k) or password(-P)")

    if args.yaml:
        stream = open(args.yaml, 'r')
        addr_list = yaml.load_all(stream)
    return addr_list


def doShit(addr_list, args):
    for dev in addr_list:
        if args.each:
            raw_input("Connecting to " + str(dev['ip']) + ". Press Enter to continue...")
        net_connect = ConnectHandler(**dev)

        if args.addvlan:
            vlans_list = args.addvlan.split()
            command_list = []
            for vlan in vlans_list:
              vlan = vlan.replace(',', '')
              command_list.append ("vlan %s" %vlan)
            output = net_connect.send_config_set(command_list)

        if args.remvlan:
            vlans_list = args.remvlan.split()
            command_list = []
            for vlan in vlans_list:
              vlan = vlan.replace(',', '')
              command_list.append ("no vlan %s" %vlan)
            output = net_connect.send_config_set(command_list)
        
        if args.storeconf:
            output = ''
            out_dir = args.storeconf
            config = net_connect.send_command("show run")
            file_ip = "%s/%s_%s.txt" % (out_dir, dev['ip'], time.strftime("%d-%m-%Y"))
            f = open(file_ip, 'w')
            f.write(config)
            f.close()
            output = "Device %s: In %s" % (dev['ip'], file_ip)

            
        if args.command:
            command = args.command
            output = net_connect.send_command(command)

        elif args.cmdfile:
            input_file = args.cmdfile
            print(input_file)
            with open(input_file) as f:
                temp = f.readlines()
                command_list = map(lambda temp: temp.strip(), temp)
                print(command_list)
                output = net_connect.send_config_set(command_list)

        elif args.test:
            output = net_connect.send_command("show users")

        print(output)

def main():
        doShit(devList(parseArgs()), parseArgs())

if __name__ == "__main__":
    main()
