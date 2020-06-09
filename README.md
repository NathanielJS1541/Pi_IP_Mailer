# Pi_IP_Mailer
This is a Python library written for the Raspberry Pi to Email the local IP address
of all network interfaces to a selected Email address when a change in any one
of the interfaces changes. This program should be run at regular intervals (of your
choice) depending on your need. It stores data in the `/tmp/` directory by default,
and it is recommended to also run this program at startup to initialise the files in
the `/tmp/` directory as they are cleared at boot.