from httpd2 import db
from sqlalchemy.dialects.postgresql import JSON


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    card = db.Column(db.String())
    flags = db.Column(db.Integer)
    tz = db.Column(db.Integer)

    def __init__(self, card, flags, tz):
        self.card = card
        self.flags = flags
        self.tz = tz

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Controller(db.Model):
    __tablename__ = 'controllers'

    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.Integer)
    type = db.Column(db.String())
    fw = db.Column(db.String())
    conn_fw = db.Column(db.String())
    active = db.Column(db.Integer)
    mode = db.Column(db.Integer)
    last_conn = db.Column(db.Integer)
    interval = db.Column(db.Integer,nullable=False ,default=10)
    license = db.Column(db.String())
    

    def __init__(self, serial, type, fw,conn_fw,active,mode, last_conn,interval, license):
        self.serial = serial
        self.type = type
        self.fw = fw 
        self.fw_conn = fw_conn
        self.active =  active
        self.mode = mode 
        self.last_conn = last_conn
        self.interval = interval
        self.license = license

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Event (db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    time  = db.Column(db.Integer, nullable=False )
    event = db.Column(db.Integer,nullable=False )
    card =   db.Column(db.String, nullable=False)
    flags = db.Column(db.Integer)

    def __init__(self, card, flags, tz):
        self.card = card
        self.flags = flags
        self.tz = tz

    def __repr__(self):
        return '<id {}>'.format(self.id)