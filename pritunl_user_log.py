import pymongo
import pprint
import bson
import time
import sys
import syslog

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['pritunl']

#
# very simple access logging on pritunl by continually monitoring the current clients list
# copyright https://github.com/DuncanRobertson 2021 GNU GENERAL PUBLIC LICENSE Version 2
#

syslogmode = False
whomode = False
stdoutmode = False

if len(sys.argv) > 1:
   if "who" in sys.argv[1:]:
       whomode = True
       stdoutmode = True

   if "syslog" in sys.argv[1:]:
       syslogmode = True

   if "stdout" in sys.argv[1:]:
       stdoutmode = True

   if not whomode and not syslogmode and not stdoutmode:
      print('''simple pritunl user log, usage:
%s [ who | syslog | stdout ]
   run continually, printing logged in users to stdout for logging, with one or more options
%s who
   run once printing a list of users currently logged in to stdout
%s syslog
   run continually, logging logged in users to syslog for logging
%s stdout 
   run continually, logging to stdout (default with no args)
''' % (sys.argv[0],sys.argv[0],sys.argv[0],sys.argv[0]))
      sys.exit(1)
else:
   stdoutmode = True


def printl(message):
   if syslogmode:
      syslog.syslog(message)
   if stdoutmode:
      print(message)

#
# this is the MongoDB version of doing a join on two tables...
# while we only pull out the fields we care about.
#
pipeline =  [{'$lookup': 
   {'from' : 'users',
    'localField' : 'user_id',
    'foreignField' : '_id',
    'as' : 'userinfo'}},
    {
       "$project" :{
          "real_address" :1, "connected_since": 1, "virt_address" : 1, "mac_addr" :1, "user_id" :1 ,
          "username" : "$userinfo.name"
       }
    }
   ]

previousclients = []
while True:

   currentclients = list(mydb.clients.aggregate(pipeline))

   if previousclients != currentclients:
      if previousclients == []:
         printl(time.asctime( time.localtime(time.time()))+" starting logger, clients connected now are:")
      else:
         printl(time.asctime( time.localtime(time.time()))+" change noted")
      for client in currentclients:
          if not client in previousclients:
             timeconnected = time.asctime(time.localtime(client['connected_since'] - time.timezone))
             printl("connected  %-17s real_address %-15s virt_address %-19s connected_since %s mac_addr %s" % \
                (client['username'][0],client['real_address'],client['virt_address'],timeconnected,client['mac_addr']))
      for client in previousclients:
          if not client in currentclients:
             timeconnected = time.asctime(time.localtime(client['connected_since'] - time.timezone))
             printl("disconnect %-17s real_address %-15s virt_address %-19s connected_since %s mac_addr %s" % \
                (client['username'][0],client['real_address'],client['virt_address'],timeconnected,client['mac_addr']))
      if not syslogmode:
         sys.stdout.flush()

   previousclients = currentclients
   if whomode:
      break
   time.sleep(1.0)
   
