import os
import sys
import time
import json
import datetime 

from flask import Flask
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

MAX_CONTENT_LEN=2000

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *

class BadRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/', methods = ['POST'])
def main():
    if request.method != 'POST':
        raise BadRequest('Not implemented', status_code=501)
    answer = []
   
    if int(request.headers.get('Content-Length') or 0) > MAX_CONTENT_LEN:
        raise  BadRequest('Too long', status_code=400)
    try:
        jsn =  request.get_json()
    except ValueError:
        raise  BadRequest('Malformed json', status_code=400)
    print ("received request: " + str(jsn), file=sys.stderr)
    sn = jsn.get('sn')
    type = jsn.get('type')
    ctrl = db.session.query(Controller).filter(Controller.serial==sn, Controller.type==type).first()
    
    for msg_json in jsn['messages']:
        operation = msg_json.get('operation')
        req_id = msg_json.get('id')
        if operation == None:
            if msg_json.get('success')== 1:
                print("ANSWER TO %d FROM CONTROLLER %d" % (req_id,sn),file=sys.stderr )
                db.session.query(Task).filter(id==req_id).delete()  
                db.session.commit()
            else:
                print("UNKNOWN ANSWER:\n%s" % (msg_json),file=sys.stderr)

        elif operation == 'power_on':
            print('CONTROLLER %d POWER ON' % sn,file=sys.stderr)
            fw = msg_json.get('fw')
            conn_fw = msg_json.get('conn_fw')
            active = msg_json.get('active')
            mode = msg_json.get('mode')
            if ctrl == None:

                print('UNKNOWN CONTROLLER ADD TO BASE',file=sys.stderr)
                controller = Controller(serial=sn,type=type, fw=fw, conn_fw=conn_fw,active=mode, last_conn=int(time.time())  )
                db.session.add(controller)
                db.session.commit()
                ctrl =  db.session.query(Controller).filter(Controller.serial==sn, Controller.type==type).first()

            else:
                controller = db.session.query(Controller).filter(Controller.serial==sn, Controller.type==type).first()
                controller.fw = fw
                controller.conn_fw = conn_fw
                controller.mode = mode
                controller.last_conn = int(time.time()),
                db.session.commit()

            if active != ctrl.active:
                answer.append(json.loads('{"id":0,"operation":"set_active","active": %d,"online": 0}' % ctrl.active))
                 
        elif operation == "ping":
            print("PING FROM CONTROLLER %d" % sn , file=sys.stderr)
            active = msg_json.get('active')
            mode = msg_json.get('mode')
            controller = db.session.query(Controller).filter(Controller.serial==sn, Controller.type==type).first()
            controller.mode = mode
            controller.last_conn = int(time.time())
            db.session.commit()  
           
            if active != ctrl.active:
                answer.append(json.loads('{"id":0,"operation":"set_active","active": %d}' % ctrl.active))
                  
        elif operation == "check_access":
            card = msg_json.get('card')
            reader = msg_json.get('reader')
            print("CHECK ACCESS FROM CONTROLLER %d [%s on %d]" % (sn,card,reader),file=sys.stderr)
            granted = 1
            answer.append(json.loads('{"id":%d,"operation":"check_access","granted":%d}' % (req_id,granted)))

        elif operation == "events":
            print("EVENTS FROM CONTROLLER %d" % sn, file=sys.stderr)
            event_cnt = 0
            for event in  msg_json.get('events'):
                event_cnt += 1
                ev_time=int(time.mktime(datetime.datetime.strptime(event.get('time'), "%Y-%m-%d %H:%M:%S").timetuple()))
                e = Event( event=event.get('event'), flags=event.get('flag'),card = event.get('card'))
                db.session.add(e)
            db.session.commit()

            print("EVENT_SUCCESS: %d" % event_cnt,file=sys.stderr)
            answer.append(json.loads('{"id":%d,"operation":"events","events_success":%d}' % (req_id,event_cnt)))

        else:
            print('UNKNOWN OERATION',file=sys.stderr)
    for task_jsn in db.session.query(Task.json).filter(Task.serial==sn, Task.type==type):
        if (len(json.dumps(answer))+len(task_jsn['json'])) > 1500:
            break
        task = json.loads(task_jsn['json'])
        task['id'] = task_jsn['id']
        answer.append(task)
    answer = '{"date":"%s","interval":%d,"messages":%s}' % (time.strftime("%Y-%m-%d %H:%M:%S"),ctrl.interval, json.dumps(answer))        
    db.session.close()
    print ("reponse:"+ answer,file=sys.stderr)
    return answer

if __name__ == '__main__':
    app.run(host='0.0.0.0')
