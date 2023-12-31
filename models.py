# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


# Create an empty SQLAlchemy object
db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))

    # genres = db.relationship(
    #    "Genre", secondary="venue_genre", backref="venues", lazy="joined"
    # )

    shows = db.relationship("Show", backref="venue", lazy="joined", cascade='all, delete')

    def __repr__(self):
        return f"<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.facebook_link} {self.website} {self.seeking_talent} {self.seeking_description}>"


class Artist(db.Model):
    __tablename__ = "artist"

    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))

    shows = db.relationship("Show", backref="artist", lazy="joined", cascade='all, delete')

    def __repr__(self):
        return f"<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.image_link} {self.facebook_link} {self.website} {self.seeking_venue} {self.seeking_description}>"

    # DONE!: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, primary_key=False)

    def __repr__(self):
        return f"<Show {self.id} {self.venue_id} {self.artist_id} {self.start_time}>"


# DONE! Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
