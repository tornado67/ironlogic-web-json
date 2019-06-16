#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sqlite3
import time
import os,binascii,json

conn = sqlite3.connect('example.sqlite')
cursor = conn.cursor()

for j in range(0,5):
    cardjson = []
    for i in range(0,15):
        cj='{"card":"'+binascii.b2a_hex(os.urandom(6))+'","flags":0,"tz":255}'
        cardjson.append(json.loads(cj))
        jsons = '{"operation":"add_cards","cards":%s}' % json.dumps(cardjson)
   
    cursor.execute("""
               INSERT INTO tasks (serial,type,json)
               VALUES (40646, 'Z5RWEB', '%s')
               """ % (jsons))
    

    results = cursor.fetchall()
    print(j)

conn.commit()
conn.close()