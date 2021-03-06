#!/usr/bin/python

from subprocess import Popen, STDOUT
from sys import stdin, exit, argv
from os import devnull

print "Content-Type: text/html"
print 

print "Starting sync script..."

if 'verbose' in argv:
	Popen(['/usr/bin/python', 'run.py'], stdin=stdin)	
else:
	with open(devnull, 'w') as fp:
		# directing stderr to stdout is essential
		# otherwise script waits for Popen to finish
		Popen(['/usr/bin/python', 'run.py'], stdin=stdin, stdout=fp, stderr=STDOUT)

print "Check http://register.geostandaarden.nl/log.txt for a status report."

exit()