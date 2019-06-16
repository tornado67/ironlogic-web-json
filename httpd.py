#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import json
import sqlite3
import time
import datetime
import ssl
import psycopg2

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_error(501, 'Not Implemented')
    def do_POST(self):
        answer = []

        #�������� ������
        msg_len = int(self.headers.getheader('Content-Length'))
        if msg_len > 2000:
            self.send_error(400, 'Bad Request length')

        msg = self.rfile.read(msg_len)

        #�������� JSON �� ����������
        try:
            jsn = json.loads(msg)
        except ValueError:
            self.send_error(400, 'Bad Request')
            return
        sn = jsn.get('sn')
        type = jsn.get('type')

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        sql_conn = sqlite3.connect('example.sqlite')
        sql_conn.row_factory = dict_factory
        cursor = sql_conn.cursor()

        #���� ���������� � ����
        cursor.execute("SELECT * FROM controllers WHERE serial = %d AND type = '%s'" % (sn,type))
        ctrl = cursor.fetchone()

        #������� ��������� �����������
        msgs_json=jsn['messages']

        for msg_json in msgs_json:
            #������� �������� �� ���������
            operation = msg_json.get('operation')
            req_id = msg_json.get('id')
            #��� ��������
            if operation == None:
                #���� ��� ����� �� ��������� �������
                if msg_json.get('success')== 1:
                    print("ANSWER TO %d FROM CONTROLLER %d" % (req_id,sn) )
                    #������� ������� ������� ������������ � ������� �� ����
                    cursor.execute("DELETE FROM tasks WHERE id = %d" % (req_id))
                    sql_conn.commit()
                else:
                    print("UNKNOWN ANSWER:\n%s" % (msg_json) )
            #���� ��� ��������� � ���������
            elif operation == 'power_on':
                print('CONTROLLER %d POWER ON' % sn)
                #������� ��������� �����������
                fw = msg_json.get('fw')
                conn_fw = msg_json.get('conn_fw')
                active = msg_json.get('active')
                mode = msg_json.get('mode')
                # ���� ���������� �� ������ � ���� ������� ���
                if ctrl == None:
                    print('UNKNOWN CONTROLLER ADD TO BASE')
                    cursor.execute("""
                                   INSERT INTO controllers (serial, type, fw, conn_fw, active, mode,last_conn)
                                   VALUES (%d, '%s', '%s' ,'%s', 0, %d, %d)
                                   """ % (sn, type, fw,conn_fw, mode, int(time.time())))
                    sql_conn.commit()
                    cursor.execute("SELECT * FROM controllers WHERE serial = %d AND type = '%s'" % (sn,type))
                    ctrl = cursor.fetchone()
                # ���� ���������� ������ � ���� �� ������� ��� ���������
                else:
                    cursor.execute("""
                                   UPDATE controllers 
                                   SET fw = '%s',conn_fw = '%s',mode = %d,last_conn = %d  
                                   WHERE serial = %d AND type = '%s'
                                   """ % (fw, conn_fw, mode, int(time.time()),  sn, type))
                    sql_conn.commit()

                #������� ����� active � ����. ���� �� ��������� � ���������� ������������ - ������ �� ��������� active
                #����� ������� �����������, ��� ������ ������������ ONLINE
                if active != ctrl.get('active'):
                    answer.append(json.loads('{"id":0,"operation":"set_active","active": %d,"online": 1}' % ctrl.get('active')))

            elif operation == "ping":
                #���������� ����������� � ����
                print("PING FROM CONTROLLER %d" % sn )
                active = msg_json.get('active')
                mode = msg_json.get('mode')
                cursor.execute("""
                                   UPDATE controllers 
                                   SET mode = %d,last_conn = %d  
                                   WHERE serial = %d AND type = '%s'
                                   """ % (mode, int(time.time()),  sn, type))
                sql_conn.commit()
                #������� ����� active � ����. ���� �� ��������� � ���������� ������������ - ������ �� ��������� active
                if active != ctrl.get('active'):
                    answer.append(json.loads('{"id":0,"operation":"set_active","active": %d}' % ctrl.get('active')))

            elif operation == "check_access":
                #�������� ������� � ������ online
                card = msg_json.get('card')
                reader = msg_json.get('reader')
                print("CHECK ACCESS FROM CONTROLLER %d [%s on %d]" % (sn,card,reader))

                #��� ������� ����� ���� ����������
                granted = 1
                answer.append(json.loads('{"id":%d,"operation":"check_access","granted":%d}' % (req_id,granted)))

                    

            elif operation == "events":
                #������ ������� � ����
                print("EVENTS FROM CONTROLLER %d" % sn )
                events = msg_json.get('events')
                event_cnt = 0;
                for event in events:
                    event_cnt += 1
                    ev_time=int(time.mktime(datetime.datetime.strptime(event.get('time'), "%Y-%m-%d %H:%M:%S").timetuple()))
                    cursor.execute("""
                                   INSERT INTO events (time,event,flags,card)
                                   VALUES (%d, %d ,%d, '%s')
                                   """ % (ev_time, event.get('event'),event.get('flag'),event.get('card')))
                    
                #������� ����������� �� �������� ������ ������� � ����
                sql_conn.commit()
                print("EVENT_SUCCESS: %d" % event_cnt)
                answer.append(json.loads('{"id":%d,"operation":"events","events_success":%d}' % (req_id,event_cnt)))
                    


            else:
                print('UNKNOWN OERATION')

        #����� ����� � ���� � ������������ ������� �����������
        for task_jsn in cursor.execute("SELECT id,json FROM tasks WHERE serial = %d AND type = '%s'" % (sn,type)):
            if (len(json.dumps(answer))+len(task_jsn['json'])) > 1500:
                break
            task = json.loads(task_jsn['json'])
            task['id'] = task_jsn['id']
            answer.append(task)
            
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        answer = '{"date":"%s","interval":%d,"messages":%s}' % (time.strftime("%Y-%m-%d %H:%M:%S"),ctrl.get('interval'),json.dumps(answer))
        self.wfile.write(answer)

        sql_conn.close()

def run():
    print('http server is starting...')
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, HTTPRequestHandler)

    httpd.socket = ssl.wrap_socket (httpd.socket,
        keyfile="key.pem",
        certfile='cert.pem', server_side=True)

    print('http server is running...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()