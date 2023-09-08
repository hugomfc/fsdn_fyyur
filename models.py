# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


# Create an empty SQLAlchemy object
db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = "venue"

    # starting in 1000 so that in the seed.py file we can use the same id for the venues
    id_seq = db.Sequence("venue_id_seq", start=1000)

    id = db.Column(
        db.Integer,
        id_seq,
        primary_key=True,
        server_default=id_seq.next_value(),
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

    genres = db.relationship(
        "Genre", secondary="venue_genre", backref="venues", lazy="joined"
    )

    shows = db.relationship("Show", backref="venue", lazy=True)

    def __repr__(self):
        return f"<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.facebook_link} {self.website} {self.seeking_talent} {self.seeking_description}>"


class VenueGenre(db.Model):
    __tablename__ = "venue_genre"
    venue_id = db.Column(
        db.Integer, db.ForeignKey("venue.id"), nullable=False, primary_key=True
    )
    genre_id = db.Column(
        db.Integer, db.ForeignKey("genre.id"), nullable=False, primary_key=True
    )

    # DONE!: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = "artist"

    # starting in 1000 so that in the seed.py file we can use the same id for the venues
    id_seq = db.Sequence("artist_id_seq", start=1000)

    id = db.Column(
        db.Integer,
        id_seq,
        primary_key=True,
        server_default=id_seq.next_value(),
        nullable=False,
        autoincrement=True,
    )
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    genres = db.relationship(
        "Genre", secondary="artist_genre", backref="artists", lazy="joined"
    )

    shows = db.relationship("Show", backref="artist", lazy=True)

    def __repr__(self):
        return f"<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.image_link} {self.facebook_link} {self.website} {self.seeking_venue} {self.seeking_description}>"

    # DONE!: implement any missing fields, as a database migration using Flask-Migrate


class Genre(db.Model):
    __tablename__ = "genre"

    # starting in 1000 so that in the seed.py file we can use the same id for the venues
    id_seq = db.Sequence("genre_id_seq", start=1000)

    id = db.Column(
        db.Integer,
        id_seq,
        primary_key=True,
        server_default=id_seq.next_value(),
        nullable=False,
        autoincrement=True,
    )
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Genre {self.id} {self.name}>"


class ArtistGenre(db.Model):
    __tablename__ = "artist_genre"
    artist_id = db.Column(
        db.Integer, db.ForeignKey("artist.id"), nullable=False, primary_key=True
    )
    genre_id = db.Column(
        db.Integer, db.ForeignKey("genre.id"), nullable=False, primary_key=True
    )

    def __repr__(self):
        return f"<ArtistGenre {self.artist_id} {self.genre_id}>"


class Show(db.Model):
    __tablename__ = "show"

    # starting in 1000 so that in the seed.py file we can use the same id for the venues
    id_seq = db.Sequence("show_id_seq", start=1000)

    id = db.Column(
        db.Integer,
        id_seq,
        primary_key=True,
        server_default=id_seq.next_value(),
        nullable=False,
        autoincrement=True,
    )
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, primary_key=False)

    def __repr__(self):
        return f"<Show {self.id} {self.venue_id} {self.artist_id} {self.start_time}>"


# DONE! Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
