Tool to manage Cisco small business switches. Uses netmiko library.  


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

