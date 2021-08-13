import pymongo
import pprint
import bson
import time
import sys
import syslog

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['pritunl']

#
# copyright https://github.com/DuncanRobertson 2021 GNU GENERAL PUBLIC LICENSE Version 2
#

allusers = False
currentusers = False

if len(sys.argv) > 1:
   if "allusers" in sys.argv[1:]:
      allusers = True

   if "currentusers" in sys.argv[1:]:
      currentusers = True

   if not allusers and not currentusers:
      print('''pritunl user mail list, usage:
   %s allusers
      list email addresses of all users, seperated by commas (default no args)
   %s currentusers
      list email addresses of all users connected to pritunl now, seperated by commas
''' % (sys.argv[0],sys.argv[0]))
      sys.exit(1)
else:
   allusers = True

if currentusers:
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
	     "username" : "$userinfo.name", "email" :  "$userinfo.email"
	  }
       }
      ]

   currentclients = list(mydb.clients.aggregate(pipeline))
   sys.stdout.write("# email addresses of user accounts currently logged into PRITUNL\n")
   firstclient = True
   for client in currentclients:
      if firstclient:
         sys.stdout.write("%s" % client['email'][0])
         firstclient = False
      else:
         sys.stdout.write(", %s" % client['email'][0])
      
   sys.stdout.write("\n")

if allusers:
   allusers = list(mydb.users.find({},{ "_id": 0, "name": 1, "email": 1}))

   sys.stdout.write("# email addresses of all PRITUNL user accounts\n")
   firstclient = True
   for user in allusers:
      if not user['email'] == None:
         if firstclient:
            sys.stdout.write("%s" % user['email'])
            firstclient = False
         else:
            sys.stdout.write(", %s" % user['email'])
   sys.stdout.write("\n")
