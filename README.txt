Tool to manage Cisco small business switches. Uses netmiko library.  

Pretty broken, mostly a work in progress. Useful for running the same commands on a bunch of Cisco small business switches at once or pulling down info. Eventually I would like to use info pulled from MAC address tables to build a web interface with drop down menus to change vlans. 


optional arguments:
  -h, --help  show this help message and exit
  -P          Prompt for SSH password. Cannot use with -k.
  -k          Use SSH keys. Requires Keyfile arg.
  -c          Runs a single command from user mode and returns result.
  -f          Reads multiple commands from <file> separated by newline and
              runs in configuration mode.
  -t          Connect to test, no commands.
  -H          Specify one individual host. Takes an IP or hostname.
  -n          Reads multiple nodes separated by newline from <file>.
  -y          Import node settings from yaml file.
  -u          User name for session.
  -i          Pause for input between each SSH session.
  -V          Toggle verbosity. Default is False. Example, -V True will turn on verbosity.
  -m          Get end device info and dump to yaml.

