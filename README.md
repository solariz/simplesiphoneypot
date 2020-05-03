# Simple Sip Honeypot and Reporter
Simple SIP Honeypot based on the abandoned honeysip project. This simple pot does not aim to be a SIP Protocol implementation to fool the "Alien Host" and keep him busy, it is more or less just logging. To avoid logging of all incoming udp requests on 5060 it do need valid SIP header requests, so a very basic check is done.

I created that script actually for my own purpose to run it on some static IPv4 I have which defenitly not runing Anything on SIP/PBX or communication and are long time in my posission. So nobody should contact this Systems with a SIP Request. I use this Script to report back to a Database and if a host found "guilty" to often I use those Data to put them in a Blacklist. This Blacklist I than use on my Real PBX Firewall to already prefilter those unwanted Hosts.

You can find the Blacklists and read more about it in a Blogpost I wrote:
[Blog post: SIP Honeypot Blacklist](https://tcpip.wtf/en/honeysip-sip-voip-ipv4-blacklist-honeypot.htm)



### Requirements

Tested on Debian 9 an Ubuntu 18. Should run on any system able to run Python3.

```
sudo apt-get -y install python3-pip screen
sudo pip3 install requests yaml-config
```


### Installation

Please make a user to run this honeypot in. Currently I do not implemented any Daemon Handling / service wrapper so it is currently neccesary to run it in a Screen or tmux whatever you prefer. As said, the script can not run as ROOT for security reasons. So please put everything in a homedir of a user created running the script. I call mine "honeypot". 

After Checkout of the latest git please make sure the requirements are installed. If you have a Firewall between WAN and your Machine please allow incoming 5060/udp. 

I recommend running fail2ban on the honeypot host, the honeypot script itself does not contain any rate limiting or connection "filtering" I do that by fail2ban reading my honeypot logfile. If a host is found 4 times in one hour fail2ban will block it for 12 hours. 

To setup fail2ban filters please have a look in the fail2ban subdirectory in the honeypot dir.

To run the actual honeypot:
```bash
# changing to user honeypot
su -s /bin/bash honeypot
# go to the dir where you put the script and run it
cd ~/honeysip
python3 sip_udp.py
```
After that you should should see output like this:
```log
python3 sip_udp.py
Listening UDP/5060...
Logging to: honeysip.log
Reporting to: https://<whatever>
```

You can detach your screen now (CTRL)-(A) -> (D)

That should be it.
