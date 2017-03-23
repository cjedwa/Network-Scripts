#!/usr/bin/python
import couchdb, parse_cisco

couch = couchdb.Server()
db = couch['cisco'] 
parsed_doc = parse_cisco.parser()[0]
#doc_rev = parse_cisco.parser()[0]["_rev"]
name = parse_cisco.parser()[1]
#f name in db:
#1    print(db.show(name))
print(name)
name = db.save(parsed_doc)
