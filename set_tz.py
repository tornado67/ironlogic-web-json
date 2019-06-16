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
               VALUES (40646, 'Z5RWEB', '{"operation":"set_timezone","zone": 0,"begin":"00:00","end":"23:59","days":"01111111"}')
               """)
conn.commit()
conn.close()