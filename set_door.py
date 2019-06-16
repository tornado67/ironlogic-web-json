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
               VALUES (40646, 'Z5RWEB', '{"operation":"set_door_params","open": 10,"open_control":10,"close_control": 10}')
               """)
conn.commit()
conn.close()