from datetime import datetime
import re

# from flask_wtf import Form
from flask_wtf import FlaskForm as Form
from wtforms import (
    StringField,
    SelectField,
    SelectMultipleField,
    DateTimeField,
    BooleanField,
    ValidationError,
)
from wtforms.validators import DataRequired, URL, Optional


state_choices = [
    ("AL", "AL"),
    ("AK", "AK"),
    ("AZ", "AZ"),
    ("AR", "AR"),
    ("CA", "CA"),
    ("CO", "CO"),
    ("CT", "CT"),
    ("DE", "DE"),
    ("DC", "DC"),
    ("FL", "FL"),
    ("GA", "GA"),
    ("HI", "HI"),
    ("ID", "ID"),
    ("IL", "IL"),
    ("IN", "IN"),
    ("IA", "IA"),
    ("KS", "KS"),
    ("KY", "KY"),
    ("LA", "LA"),
    ("ME", "ME"),
    ("MT", "MT"),
    ("NE", "NE"),
    ("NV", "NV"),
    ("NH", "NH"),
    ("NJ", "NJ"),
    ("NM", "NM"),
    ("NY", "NY"),
    ("NC", "NC"),
    ("ND", "ND"),
    ("OH", "OH"),
    ("OK", "OK"),
    ("OR", "OR"),
    ("MD", "MD"),
    ("MA", "MA"),
    ("MI", "MI"),
    ("MN", "MN"),
    ("MS", "MS"),
    ("MO", "MO"),
    ("PA", "PA"),
    ("RI", "RI"),
    ("SC", "SC"),
    ("SD", "SD"),
    ("TN", "TN"),
    ("TX", "TX"),
    ("UT", "UT"),
    ("VT", "VT"),
    ("VA", "VA"),
    ("WA", "WA"),
    ("WV", "WV"),
    ("WI", "WI"),
    ("WY", "WY"),
]

genre_choices = [
    ("Alternative", "Alternative"),
    ("Blues", "Blues"),
    ("Classical", "Classical"),
    ("Country", "Country"),
    ("Electronic", "Electronic"),
    ("Folk", "Folk"),
    ("Funk", "Funk"),
    ("Hip-Hop", "Hip-Hop"),
    ("Heavy Metal", "Heavy Metal"),
    ("Instrumental", "Instrumental"),
    ("Jazz", "Jazz"),
    ("Musical Theatre", "Musical Theatre"),
    ("Pop", "Pop"),
    ("Punk", "Punk"),
    ("R&B", "R&B"),
    ("Reggae", "Reggae"),
    ("Rock n Roll", "Rock n Roll"),
    ("Soul", "Soul"),
    ("Other", "Other"),
]


class ShowForm(Form):
    artist_id = StringField("artist_id")
    venue_id = StringField("venue_id")
    start_time = DateTimeField(
        "start_time", validators=[DataRequired()], default=datetime.today()
    )


class ContactForm(Form):
    name = StringField("name", validators=[DataRequired()])
    state = SelectField(
        "state",
        validators=[DataRequired()],
        choices=state_choices,
    )
    city = StringField("city", validators=[DataRequired()])
    phone = StringField("phone", validators=[DataRequired()])

    def validate_phone(self, phone):
        """validate phone numbers like:
        123-456-7890
        1234567890
        123 456 7890
        """
        pattern = re.compile(r"^\d{3}[-\s]?\d{3}[-\s]?\d{4}$")
        if not pattern.match(phone.data):
            raise ValidationError("Invalid phone number.")

    facebook_link = StringField("facebook_link", validators=[Optional(), URL()])
    website_link = StringField("website_link", validators=[Optional(), URL()])


class VenueForm(ContactForm):
    image_link = StringField("image_link", validators=[Optional(), URL()])
    genres = SelectMultipleField(
        # DONE! implement enum restriction
        "genres",
        validators=[DataRequired()],
        choices=genre_choices,
    )

    address = StringField("address", validators=[DataRequired()])
    seeking_talent = BooleanField("seeking_talent")

    seeking_description = StringField("seeking_description")

    def validate_seeking_description(self, seeking_description):
        if self.seeking_talent.data == True and not self.seeking_description.data:
            raise ValidationError(
                "Please provide a description of what you are looking for."
            )


class ArtistForm(ContactForm):
    # DONE! implement validation logic for phone

    image_link = StringField("image_link", validators=[Optional(), URL()])
    genres = SelectMultipleField(
        "genres",
        validators=[DataRequired()],
        choices=genre_choices,
    )
    # DONE! implement enum restriction

    seeking_venue = BooleanField("seeking_venue")

    seeking_description = StringField("seeking_description")

    def validate_seeking_description(self, seeking_description):
        if self.seeking_venue.data == True and not self.seeking_description.data:
            raise ValidationError(
                "Please provide a description of what you are looking for."
            )
