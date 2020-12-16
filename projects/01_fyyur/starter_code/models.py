#----------------------------------------------------------------------------#
# Imports.
#----------------------------------------------------------------------------#
import json
from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_talent_description = db.Column(db.String())
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy='dynamic')
    # TODO: add functions needed as insert, update, delete, description
    def __repr__(self):
      return f'<venue {self.id} {self.name} >'

    def row2dict(row):
      return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_venue_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy='dynamic')
    # TODO: add functions needed as insert, update, delete, description
    def __repr__(self):
      return f'<Venue {self.id} {self.name} >'

    def row2dict(row):
      return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())

#TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # TODO: add functions needed as insert, update, delete, description
    def __repr__(self):
      return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id} and Start Time {self.start_time}>'
    def row2dict(row):
      return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())