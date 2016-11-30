#!/usr/bin/env python
from __future__ import print_function
import sys, argparse, datetime, getpass, yaml
from netmiko import ConnectHandler
from netmiko.cisco import CiscoS300SSH

def main():

    parser = argparse.ArgumentParser(description='sgtool: Program to configure simplify configuration of Cisco SG300 Switches.\nAuthor: Cody Edwards\n cjedwa@sandia.gov')

    authgroup = parser.add_mutually_exclusive_group()
    authgroup.add_argument('-P', action="store_true", help='Prompt for SSH password.')
    authgroup.add_argument('-k', action='store', help='Use SSH keys. Requires Keyfile arg if not in standard spot.' )

    commandgroup = parser.add_mutually_exclusive_group()
    commandgroup.add_argument('-c', nargs='?', help='Runs a single command from user mode')
    commandgroup.add_argument('-f', nargs='?', help='Reads multiple commands from <file> separated by newline and runs in configuration mode')
    commandgroup.add_argument('-t', action="store_true" ,help='Connect to test, no commands.')

    hostgroup = parser.add_mutually_exclusive_group()
    hostgroup.add_argument('-H', help='Runs commands specified by -c or -f on a single host. Takes an IP addr or resolvable name.')
    hostgroup.add_argument('-n', help='Reads multiple nodes separated by newline from <file>.')
    hostgroup.add_argument('-y', help='Import node settings from yaml file.')

    parser.add_argument('-u', default=getpass.getuser(), help='User name for session.')
    parser.add_argument('-i', action="store_true", help='Pause for input between multiple SSH sessions.')
    parser.add_argument('-V', default=False, help='Toggle verbosity')

    args = parser.parse_args() 


    addr_list = []

    if args.u:
        uname = args.u

    if args.n:
        with open(args.n) as f:
            temp = f.readlines()
            node_list = map(lambda temp: temp.strip(), temp)
            if args.k:
                for i in node_list:
                    addr_list.append( 
                        {
                        'device_type': 'cisco_s300',
                        'ip':   i,
                        'username': str(uname),
                        'password': str(password),
                        'port' : 22,        
                        'verbose': args.V,
                        'use_keys': True,
                        'key_file': args.k
                        }
                    )
            elif args.P:
                password = getpass.getpass(prompt="Enter Password: ")
                for i in node_list:
                    addr_list.append( 
                        {
                        'device_type': 'cisco_s300',
                        'ip':   i,
                        'username': str(uname),
                        'password': str(password),
                        'port' : 22,        
                        'verbose': args.V,
                        'use_keys': False,
                        }
                    )

    if args.H:
        if args.k:
            addr_list.append( 
                {
                'device_type': 'cisco_s300',
                'ip': args.H,
                'username': str(uname),
                'password': str(password),
                'port' : 22,        
                'verbose': args.V,
                'use_keys': True,
                'key_file': args.k
                }
            )
            print("k")
        elif args.P:
            password = getpass.getpass(prompt="Enter Password: ")
            addr_list.append( 
                {
                'device_type': 'cisco_s300',
                'ip': args.H,
                'username': str(uname),
                'password': str(password),
                'port' : 22,        
                'verbose': args.V,
                'use_keys': False,
                }
            )
            print("P")

    if args.y:
        stream = open(args.y, 'r')
        addr_list = yaml.load_all(stream)

    for i in addr_list:
        if args.i:
            raw_input("Connecting to " + str(i['ip']) + ". Press Enter to continue...")

        net_connect = ConnectHandler(**i)

        if args.c:
            command = args.c
            output = net_connect.send_command(command)
            print(output)

        elif args.f:
            input_file = args.f
            print(input_file)
            with open(input_file) as f:
                temp = f.readlines()
                command_list = map(lambda temp: temp.strip(), temp)
                print(command_list)
                output = net_connect.send_config_set(command_list)
                print(output)

        elif args.t:
            net_connect.find_prompt() 
        end_time = datetime.datetime.now().time()
    #    delta = start_time - end_time
    #    print(delta.total_seconds())

if __name__ == "__main__":
   main()