'''
===========================================================================================
duckdns.py
By Aaron White

Written for Python 2.7

ABOUT
- DuckDNS script to update dynamic IP addresses with the DuckDNS DDNS servers. 
- Requires duckdns account and secret token for updating.  
- Works with any Unix based system.

DuckDNS is a free Dynamic Domain Name Service (DDNS) that can be used to associate a specific 
IP address to a normal domain name.  Ex- If the current external IP for your machine is 200.1.2.3, 
the script can update the IP address with DuckDNS and your registered hostname of "aaron.duckdns.org"

More information on DuckDNS can be found at http://www.duckdns.org/why.jsp

This is primarily useful when an Internet Service Provider uses Dynamic IP addresses that can 
change regularly. 

Automating the update:
Once the identifying information has been entered, uncomment final line and add to user crontab 
for automatic updating.  For dynamic IP addresses that change frequently, use a shorter timeframe 
(every hour or even every few minutes).  If address changes less frequently, use a longer timeframe 
(every six or twelve hours). 
===========================================================================================
'''

from time import strftime
from bs4 import BeautifulSoup as bs
from subprocess import call
import os.path

try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen
	
domains = ""	# Separated by a comma. No spaces.
token = "token_from_duckdns"
path= "/path/to/update/duckdns/script/folder/" # used for log files	
url = "https://www.duckdns.org/update?domains="+domains+"&token="+token+"&ip="
ip = "http://checkip.dyndns.org/"



def update():
	# Check if log exists, grab last IP address on file, and clean log if too long. 
	if os.path.isfile(path+'.duckdns.log'): 
		# Open log file and check length
		d = open(path + '.duckdns.log', 'r')
		log = d.readlines()
		lastline = log[len(log)-1]
		lastip = lastline.split()[3] # Last IP address on file
		d.close()
	
		# Clean log file if there are more than 20 lines to prevent log from growing too large. 
		if len(log) > 20:
			d = open(path+'.duckdns.log', 'w')
			d.write('New log started at '+ strftime("%Y-%m-%d %H:%M:%S") + "\n")
			d.write('Previous:\n')
			d.write(lastline) # Add last line from previous log file. 
			d.close()
			
	else: # If no log exists Last IP address is set to NA
		lastip = "NA" 

	# Check current IP address from DynDNS
	try:
		ipr = urlopen(ip)
		ipaddress= ipr.read()
		ipr.close()
	
		ipaddress = bs(ipaddress).body.get_text() # Remove HTML tags using BeautifulSoup
		newip = ipaddress.split()[3].encode('utf8', 'ignore') # Current IP address
	except:
# 		call(['terminal-notifier', '-message', "no internet connection", '-title', '"DuckDNS updater"']) 
		quit()
	# Compare current IP to last IP stored in log
	if lastip == newip: # No change in IP address

		# Notify of no change. Commented out because not necessary after debugging. 
# 		call(['terminal-notifier', '-message', "nothing to update", '-title', '"DuckDNS"']) 
		return lastip
		
	else:	# IP address has changed.  Write new IP to file and update duckdns server. 
		r = urlopen(url) # Open duckdns page to update IP.
		response= r.read() # Response from duckdns.  
		r.close()
		
		with open(path + ".duckdns.log", "a") as log: # Write new IP address to log file. 
			log.write(ipaddress + " updated at " + strftime("%Y-%m-%d %H:%M:%S") + " status: " + response + "\n")
			log.close()
		message = "IP updated to " + newip
		# Send message to Notification Center that IP has been updated (Mac only)
		# call(['terminal-notifier', '-message', message, '-title', '"DuckDNS IP address updated"']) 
		return newip

update()
