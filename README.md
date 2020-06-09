# Pi_IP_Mailer
This is a Python library written for the Raspberry Pi to Email the local IP address
of all network interfaces to a selected Email address when a change in any one
of the interfaces changes. This program should be run at regular intervals (of your
choice) depending on your need. It stores data in the `/tmp/` directory by default,
and it is recommended to also run this program at startup to initialise the files in
the `/tmp/` directory as they are cleared at boot.

## Requirements
* **`cron`** - For this to work as intended, you will need to schedule tasks with `cron`
(detailed instructions below)
* **A Gmail account** - just because you _can_ use an existing Gmail account for
this doesn't mean that you _should_. It is recommended that you create a **NEW** Gmail
account specifically for this purpose since the password for the account will be stored in
**plaintext** and I am unable to find a way around this. You will also need to enable
the Gmail API (Details to follow), which reduces the security of your account.
* **Python 3**

## Setup
### Account Configuration
After (hopefully) creating a new Gmail account (without 2FA unless you know how to modify 
the code), you need to turn **ON** _Less secure app access_ under the _Security_ tab of 
_Manage My Account_. This allows the Python code send and receive Emails using your Gmail
account.

Next, move the script (`Pi_IP_Mailer.py`) somewhere permanent on your Raspberry Pi, and
open it with a text editor such as nano: `nano Pi_IP_Mailer.py`. You need to add your new 
Gmail account and password into the `email_notification` function. Put your new Gmail address
at the variable `gmail_user` and the plaintext password at `gmail_password`. You should also
change `to` to be the email you want to receive the notifications to. You can now press `Ctrl + X`
to exit nano, and press `y` to save your changes.

Finally, ensure that the script is executable by typing `sudo chmod +X Pi_IP_Mailer.py` into
the terminal.

### Script Execution
This python script is intended to be run at startup, and then at regular intervals whenever the
Pi is running. This is only a guide, and if you know what you are doing feel free to change this.
#### Startup
When the Pi first boots, the `/tmp/` directory is empty. Since the script relies on the data within
`/tmp/` to detect changes, it is wise to run the program at startup to add relevant files to this
directory. This also has the effect that whenever the Pi Reboots or turns on, it will send it's IP
address to your email, regardless of whether it changed last time or not. If you do not want this, 
edit the script and change `TEMP_ADDRESS_DIR` to be somewhere else, such as `/home/pi/Documents/`.

In order to get the script to run at startup, open a terminal and type in `sudo nano /etc/rc.local`.
This should bring up an existing file which looks something like this:
```bash
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

exit 0
```
Simply add the following line: `python /home/pi/Documents/Pi_IP_Mailer.py` above the `printf`
line (Remembering to change the path to match where you saved your script) and save the file. The file
should now look like this:
```bash
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  python /home/pi/Documents/Pi_IP_Mailer.py
  printf "My IP address is %s\n" "$_IP"
fi

exit 0
```

If you want to test this, `sudo reboot` your Pi and you should get an Email. If you don't, check that you
entered your gmail details by simply running the script with `python Pi_IP_Mailer.py`. If you still don't
get an Email, and you checked your spam folders, there is a problem with your Gmail details or account.

#### Task Scheduling
The easiest way to schedule tasks on a Raspberry Pi is to use `cron`. Simply type `crontab -e` into a 
terminal. I chose to run this script every half an hour, so to do this add the following line to the bottom
of the file:
```
*/30 * * * * python /home/pi/Documents/Pi_IP_Mailer/Pi_IP_Mailer.py
```
Remember to change the path to match that of your script. If you wanted the script to run every 5 minutes
you would change `*/30` to `*/5`. If you wanted the script to run every hour the line would instead look like
this:
```
* */1 * * * python /home/pi/Documents/Pi_IP_Mailer/Pi_IP_Mailer.py
```
I aim with these examples to provide quick and easy setup of the script, not a full tutorial in how to use cron.
The man pages are very helpful if you would like to learn more and can be found by typing `man crontab`.

## Other References
If this isn't quite what you were looking for, try looking at some of these instead:
* [MathWorks' Tutorial to send an email when an IP address changes using ssmtp](https://uk.mathworks.com/help/supportpkg/raspberrypi/ug/configure-raspberry-pi-hardware-to-email-ip-address-changes.html "MathWorks")
