import subprocess
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import socket
import os

"""
For this program to work some setup on your Raspberry Pi is required. First ensure that the program is executable:
sudo chmod +X Pi_IP_Mailer.py

Then use cron to schedule this to run regularly (this example will run the task every hour on the hour):
Type into the terminal "cron -e".
Then add this line at the bottom of your cron file, remembering to edit the path correctly:
00 * * * * /usr/bin/python3 /home/pi/Documents/Pi_IP_Mailer.py

It is also recommended to run this at startup (and it will always email you when the Pi powers on in this case,
as the /tmp/ dir is cleared on a power cycle):

Enter "sudo nano /etc/rc.local" into a terminal.
Edit the file to look something like this (remembering to edit the path if required):

_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  sleep 20
  /usr/bin/python3 /home/pi/Documents/Pi_IP_Mailer/Pi_IP_Mailer.py
  printf "My IP address is %s\n" "$_IP"
fi

exit 0

The sleep 20 is not always needed, but in some instances the network interface may not initialise before the script
runs, so the script will fail without the delay. Alternatively the if statement may be causing a problem, so removing
that could help:

sleep 20
/usr/bin/python3 /home/pi/Documents/Pi_IP_Mailer/Pi_IP_Mailer.py

The program will now work as intended. It is also worth noting that storing passwords in plaintext is BAD. PLEASE
create a new email address for this program that is not linked to any of your other accounts and has a unique
password. You will also need to go to your Gmail "Manage your account" settings and under "security" turn access for
"Less secure apps" ON. PLEASE create a separate email for this reason.
"""

# Directory to store persistent files in between runs of this program
TEMP_ADDRESS_DIR = '/tmp/'


# Function to send an email to the specified account
def email_notification(email_body):
    # Account Details
    to = 'YourEmail@gmail.com'                         # The email will be sent to this address
    gmail_user = 'PiEmail@gmail.com'                   # Gmail account that the email will be sent from
    gmail_password = 'PASSWORD'                        # Gmail password.
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)  # This is the smtp server to use

    smtp_server.ehlo()                             # Identify device to ESMTP server
    smtp_server.starttls()                         # Start TLS encryption
    smtp_server.ehlo()
    smtp_server.login(gmail_user, gmail_password)  # Log in to server

    # Compose the message
    email = MIMEText(email_body)
    email['Subject'] = '%s on %s' % (socket.gethostname(), datetime.now().strftime('%d/%m/%Y at %H:%M'))
    email['From'] = gmail_user
    email['To'] = to

    # Send the message
    smtp_server.sendmail(gmail_user, [to], email.as_string())

    # Close connection to server
    smtp_server.quit()


# Write the current IP address to a file named after the interface. There will be one file per iface
def write_ip_file(dev, ip, write_mode):
    temp_file = open(TEMP_ADDRESS_DIR + 'IP_History_%s.txt' % dev, write_mode)
    temp_file.write(ip)
    temp_file.close()


# Read the old IP address to the interface specific file
def read_ip_file(dev):
    temp_file = open(TEMP_ADDRESS_DIR + 'IP_History_%s.txt' % dev, 'r')
    old_ip = temp_file.read()
    temp_file.close()
    return old_ip


# Detect a change in IP address. Returns "True" if a change is detected.
def detect_ip_change(dev, ip):
    # If the file does not exist (due to reboot etc. as /tmp/ is cleared), create the file and flag change
    if not os.path.isfile(TEMP_ADDRESS_DIR + 'IP_History_%s.txt' % dev):
        write_ip_file(dev, ip, 'w')
        return True

    # If the file does exist, read IP from it and detect a change in IP.
    last_ip = read_ip_file(dev)
    if last_ip != ip:
        # IP has changed
        write_ip_file(dev, ip, 'w')
        return True
    else:
        # IP is the same
        return False


arg = 'ip route list'                                          # Linux command to list interfaces and IP's
p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)  # Runs 'arg' in a 'hidden terminal'.
data = p.communicate()                                         # Get data from 'p terminal'.

message_body = ""                # Start with a blank message body
change_detected = False          # Start with no changes detected
ip_lines = data[0].splitlines()  # Take the input data and split it by line
"""
data will look something like this:
-----------------------------------------------------------------------------------
default via XXX.XXX.XXX.XXX dev usb0 src XXX.XXX.XXX.XXX metric XXX 
default via XXX.XXX.XXX.XXX dev wlan0 src XXX.XXX.XXX.XXX metric XXX 
XXX.XXX.XXX.XXX/XX dev wlan0 proto kernel scope link src XXX.XXX.XXX.XXX metric XXX 
XXX.XXX.XXX.XXX/XX dev usb0 proto kernel scope link src XXX.XXX.XXX.XXX metric XXX 
-----------------------------------------------------------------------------------

The first two lines are giving details about the default routes for any packet. We
want to ignore these lines.
Every interface will have a line after the list of defaults. Therefore, we can look
for the word "default" in each line, and if we don't find it we can process the line.
"""
for i in range(0, len(ip_lines)):
    if b'default' not in ip_lines[i]:
        split_line = ip_lines[i].split()  # Split the line into individual words
        """
        The interface name always follows the word "dev", therefore it will be at the index
        after that of the word "dev". It is currently a byte literal, so we convert it into a
        string by decoding it from the UTF-8 format.
        """
        interface_name = split_line[split_line.index(b'dev')+1].decode('utf-8')
        """
        The IP address for that interface always follows the word "src". The same idea
        as before is used, remembering to use the .decode() function.
        """
        assigned_ip = split_line[split_line.index(b'src')+1].decode('utf-8')
        change_detected += detect_ip_change(interface_name, assigned_ip)  # Keep track of any detected changes
        message_body += '%s has been assigned the IP: %s\n' % (interface_name, assigned_ip)  # Compose the email

if change_detected >= True:
    # Only send an email if at least one change has been detected.
    email_notification(message_body)
