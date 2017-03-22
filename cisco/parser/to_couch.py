#!/usr/bin/python
import couchdb, json
couch = couchdb.Server()
db = couch['cisco'] 
conf_file = open('./config.json', 'r')
doc = json.dumps(conf_file)
print(doc)
