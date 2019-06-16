#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sqlite3
import time
import os,binascii,json

conn = sqlite3.connect('example.sqlite')
cursor = conn.cursor()
cursor.execute("""
               INSERT INTO tasks (serial,type,json)
               VALUES (40646, 'Z5RWEB', '{"operation":"add_cards","cards":[{"card": "A8C19E002900","flags": 0,"tz": 255}]}')
               """)
conn.commit()
conn.close()