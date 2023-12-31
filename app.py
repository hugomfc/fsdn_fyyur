# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Show, Venue, Artist

# from flask_wtf import csrf
from flask_wtf.csrf import CSRFProtect

from datetime import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


csrf = CSRFProtect()
app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db.init_app(app)
csrf.init_app(app)
migrate = Migrate(app, db)

# DONE! connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # DONE!: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []

    venues_shows = (
        db.session.query(
            Venue.city,
            Venue.state,
            Venue.id,
            Venue.name,
            func.count(Show.id).label("num_upcoming_shows"),
        )
        .outerjoin(Show)
        # .filter(Show.start_time > datetime.now())
        .group_by(Venue.city, Venue.state, Venue.id, Venue.name)
        .order_by("num_upcoming_shows", Venue.city, Venue.state, Venue.id, Venue.name)
        .all()
    )

    # if len(venues_upcoming_shows) > 0:
    city = venues_shows[0].city
    state = venues_shows[0].state
    venues = []
    for venue in venues_shows:
        if city != venue.city or state != venue.state:
            data.append({"city": city, "state": state, "venues": venues})
            city = venue.city
            state = venue.state
            venues = []
        venues.append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": venue.num_upcoming_shows,
            }
        )
    data.append({"city": city, "state": state, "venues": venues})

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # DONE!: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get("search_term", "")

    search_results = (
        db.session.query(
            Venue.city,
            Venue.name,
            Venue.id,
            func.count(Show.id).label("num_upcoming_shows"),
        )
        .filter(Venue.name.ilike(f"%{search_term}%"))
        .group_by(Venue.city, Venue.state, Venue.id, Venue.name)
        .order_by("num_upcoming_shows", Venue.city, Venue.state, Venue.id, Venue.name)
        .all()
    )

    data = []
    for venue in search_results:
        data.append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": venue.num_upcoming_shows,
            }
        )

    response = {
        "count": len(search_results),
        "data": data,
    }
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE!: replace with real venue data from the venues table, using venue_id

    data = {}
    past_shows = []
    upcoming_shows = []

    venue = Venue.query.get_or_404(venue_id)
    venue_shows = (
        db.session.query(
            Artist.id.label("artist_id"),
            Artist.name.label("artist_name"),
            Artist.image_link.label("artist_image_link"),
            Show.start_time.label("start_time"),
        )
        .join(Artist)
        .join(Venue)
        .filter(Venue.id == venue_id)
    )

    for show in venue_shows:
        show_data = {
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if show.start_time <= datetime.now():
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # DONE!: insert form data as a new Venue record in the db, instead
    # DONE!: modify data to be the data object returned from db insertion

    form = VenueForm(request.form)

    if not form.validate():
        message = []
        for field, errors in form.errors.items():
            message.append(field + ": " + ", ".join(errors))
        flash("Please fix the following errors: " + ", ".join(message))
        return render_template("forms/new_venue.html", form=form)

    try:
        print(request.form)
        new_venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website=form.website_link.data,
            seeking_talent=(
                "seeking_talent" in request.form and form.seeking_talent.data == "y"
            ),
            # seeking_talent=request.form["seeking_talent"],
            seeking_description=form.seeking_description.data,
            genres=form.genres.data,
        )

        # for genre in request.form.getlist("genres"):
        #    genre = Genre.query.filter_by(name=genre).first()
        #    new_venue.genres.append(genre)

        db.session.add(new_venue)
        db.session.commit()

        # on successful db insert, flash success
        flash("Venue " + request.form["name"] + " was successfully listed!")

    except Exception as e:
        db.session.rollback()
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        print(e)
    # DONE!: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<int:venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # DONE!: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash(f"Venue {venue_id} was successfully deleted!")
        return jsonify({"redirect": url_for("index")})
    except Exception as e:
        print(e)
        db.session.rollback()
        flash(f"An error occurred. Venue {venue_id} could not be deleted.")
        # return render_template("pages/show_venue.html", venue=venue_id)
        return jsonify({"error": str(e)}), 500


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # DONE!: replace with real data returned from querying the database

    data = []

    artists = Artist.query.all()

    if artists:
        data = [
            {
                "id": artist.id,
                "name": artist.name,
            }
            for artist in artists
        ]

    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # DONE!: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_terms = request.form.get("search_term", "")
    search_results = (
        db.session.query(
            Artist.id, Artist.name, func.count(Show.id).label("num_upcoming_shows")
        )
        .filter(Artist.name.ilike(f"%{search_terms}%"))
        .group_by(Artist.id, Artist.name)
        .order_by(Artist.id, Artist.name)
        .all()
    )

    response = {
        "count": len(search_results),
        "data": [
            {
                "id": result.id,
                "name": result.name,
                "num_upcoming_shows": result.num_upcoming_shows,
            }
            for result in search_results
        ],
    }

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # DONE!: replace with real artist data from the artist table, using artist_id

    data = {}
    past_shows = []
    upcoming_shows = []

    artist = Artist.query.get_or_404(artist_id)

    artist_shows = (
        db.session.query(
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
            Venue.image_link.label("venue_image_link"),
            Show.start_time.label("start_time"),
        )
        .join(Artist)
        .join(Venue)
        .filter(Artist.id == artist_id)
    )

    for show in artist_shows:
        show_data = {
            "venue_id": show.venue_id,
            "venue_name": show.venue_name,
            "venue_image_link": show.venue_image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if show.start_time <= datetime.now():
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    # DONE!: populate form with fields from artist with ID <artist_id>

    artist = Artist.query.get_or_404(artist_id)
    if artist:
        form.name.data = artist.name
        form.genres.data = artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website_link.data = artist.website
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # DONE!: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm(request.form)
    artist = Artist.query.get_or_404(artist_id)

    if not form.validate():
        message = []
        for field, errors in form.errors.items():
            message.append(field + ": " + ", ".join(errors))
        flash("Please fix the following errors: " + ", ".join(message))
        return render_template("forms/edit_artist.html", form=form, artist=artist)

    if artist:
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.image_link = form.image_link.data
            artist.facebook_link = form.facebook_link.data
            artist.website = form.website_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.genres = form.genres.data

            db.session.commit()
            flash("Artist " + request.form["name"] + " was successfully updated!")
        except Exception as e:
            db.session.rollback()
            flash(
                "An error occurred. Artist "
                + request.form["name"]
                + " could not be updated."
            )
            print(e)

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    # DONE!: populate form with values from venue with ID <venue_id>

    venue = Venue.query.get_or_404(venue_id)

    if venue:
        form.name.data = venue.name
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website_link.data = venue.website
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
        form.image_link.data = venue.image_link

    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # DONE!: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm(request.form)
    venue = Venue.query.get_or_404(venue_id)

    if not form.validate():
        message = []
        for field, errors in form.errors.items():
            message.append(field + ": " + ", ".join(errors))
        flash("Please fix the following errors: " + ", ".join(message))
        return render_template("forms/edit_venue.html", form=form, venue=venue)

    if venue:
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.facebook_link = form.facebook_link.data
            venue.website = form.website_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data

            venue.genres = form.genres.data

            db.session.commit()
            flash("Venue " + request.form["name"] + " was successfully updated!")
        except Exception as e:
            db.session.rollback()
            flash(
                "An error occurred. Venue "
                + request.form["name"]
                + " could not be updated."
            )
            print(e)

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # DONE!: insert form data as a new Venue record in the db, instead
    # DONE!: modify data to be the data object returned from db insertion

    form = ArtistForm(request.form)

    if not form.validate():
        message = []
        for field, errors in form.errors.items():
            message.append(field + ": " + ", ".join(errors))
        flash("Please fix the following errors: " + ", ".join(message))
        form = ArtistForm()
        return render_template("forms/new_artist.html", form=form)

    try:
        new_artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
            genres=form.genres.data,
        )

        db.session.add(new_artist)
        db.session.commit()

        # on successful db insert, flash success
        flash("Artist " + new_artist.name + " was successfully listed!")
    except Exception as e:
        # DONE!: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        db.session.rollback()
        flash("An error occurred. Artist " + form.name.data + " could not be listed.")
        print(e)

    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # DONE!: replace with real venues data.

    shows = Show.query.order_by(Show.start_time).all()
    shows_data = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for show in shows
    ]

    return render_template("pages/shows.html", shows=shows_data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    form = ShowForm(request.form)

    if not form.validate():
        message = []
        for field, errors in form.errors.items():
            message.append(field + ": " + ", ".join(errors))
        flash("Please fix the following errors: " + ", ".join(message))
        form = ShowForm()
        return render_template("forms/new_show.html", form=form)

    try:
        new_show = Show(
            venue_id=form.venue_id.data,
            artist_id=form.artist_id.data,
            start_time=form.start_time.data,
        )

        db.session.add(new_show)
        db.session.commit()

        # on successful db insert, flash success
        flash("Show was successfully listed!")
    except Exception as e:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash("An error occurred. Show could not be listed.")
        print(e)

    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
