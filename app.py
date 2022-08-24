#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import logging
import sys
from datetime import *
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import (Flask, Response, abort, flash, redirect, render_template,
                   request, url_for)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from pyparsing import traceback
from sqlalchemy import *

from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

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
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(200)))
    website_link = db.Column(db.String(200))
    talent_search = db.Column(db.Boolean, default = False)
    description =  db.Column(db.String(200))
    showing_venue = db.relationship('Shows', backref = 'Venue', lazy = True , cascade ='all,delete' ) 


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(200))
    venue_seek = db.Column(db.Boolean, default = False)
    description = db.Column(db.String(200))
    showing_artist = db.relationship('Shows', backref = 'Artist', lazy = True , cascade ='all,delete') 

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Shows(db.Model):
  __tablename__ = "Shows"

  show_id = db.Column(db.Integer, primary_key = True)
  venue_id = db.Column(db.Integer, ForeignKey(Venue.id))
  artist_id = db.Column(db.Integer, ForeignKey(Artist.id))
  start_time = db.Column(db.DateTime, nullable = False)

class test(db.Model):


  id = db.Column(db.Integer, primary_key = True)
  name =db.Column(db.String(120))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  #select all venues grouped by the same city and state
  distinct_venues = Venue.query.distinct(Venue.state, Venue.city).all()

  if not distinct_venues:
    flash("No Venues to show at the moment:)")

  data = []
  #for each distinct venue query for venues with the same city and state
  
  for venue in distinct_venues:
    venue_show = []
    #get all results with the same city and state
    assigned_venue = Venue.query.filter_by(city = venue.city,state = venue.state).all()
    #add each venue to the list
    for putting in assigned_venue:
      venue_show.append(putting)

    data.append({
      "city" : venue.city,
      "state" : venue.state,
      "venues" : venue_show
    })


  
  
  
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"



  #get the entered search term
  searched_term = request.form.get('search_term', '')
  #get results from the Venue table having the search keyword
  search_result = Venue.query.filter(Venue.name.ilike("%{}%".format(searched_term))).all()

  search_data = []
  for venue_shown in search_result:
    search_data.append({
      "id" : venue_shown.id,
      "name" : venue_shown.name
    })

  response = {
    "count" : len(search_result),
    "data" : search_data
  }





  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  showVenue = Venue.query.get(venue_id)

  pastShow = db.session.query(Shows).join(Venue).filter(venue_id ==Venue.id).filter(Shows.start_time<datetime.now()).all()
  UpcomingShow = db.session.query(Shows).join(Venue).filter(venue_id ==Venue.id).filter(Shows.start_time>=datetime.now()).all()
  pastShowCount = len(pastShow)
  UpcomingShowCount = len(UpcomingShow)

  print(showVenue)

  pastShowList = []
  for past in  pastShow:
    artist_values = Artist.query.get(past.artist_id)
    things = {
      "artist_id" : past.artist_id,
      "artist_name" : artist_values.name,
      "artist_image_link" : artist_values.image_link,
      "start_time" : str(past.start_time),

    }

    pastShowList.append(things)

  upcomingShowList = []
  for upcoming in  UpcomingShow:
    artist_values_upcoming = Artist.query.get(upcoming.artist_id)
    upcoming_things = {
      "artist_id" : upcoming.artist_id,
      "artist_name" : artist_values_upcoming.name,
      "artist_image_link" : artist_values_upcoming.image_link,
      "start_time" : str(upcoming.start_time),

    }

    upcomingShowList.append(upcoming_things)
  
  

  data = {
    "id" : venue_id,
    "name" : showVenue.name,
    "genres" : showVenue.genres,
    "address" : showVenue.address,
    "city" : showVenue.city,
    "state" : showVenue.state,
    "phone" : showVenue.phone,
    "website" : showVenue.website_link,
    "facebook_link" : showVenue.facebook_link,
    "seeking_talent" : showVenue.talent_search,
    "seeking_description": showVenue.description,
    "image_link" : showVenue.image_link,
    "past_shows" : pastShowList,
    "upcoming_shows" : upcomingShowList,
    "past_shows_count" : pastShowCount,
    "upcoming_shows_count" : UpcomingShowCount

  }
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate():
    error_occur =False
    try:
      venue_add = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        genres = form.genres.data,
        website_link = form.website_link.data,
        talent_search = form.seeking_talent.data,
        description = form.seeking_description.data
      )
      db.session.add(venue_add)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      error_occur = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      if error_occur:
        abort(400)
  
  else:
    warning = []
    for k,v in form.errors.items():
      warning.append(k + ' ' + '/'.join(v))
    flash('Ooops!!! '+str(warning) )

    




  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    Venue.query.get(venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists_list = Artist.query.distinct(Artist.name).all()


  data = []
  for values in artists_list:
    data.append({
      "id" : values.id,
      "name" : values.name
    })






  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  searched_artist = request.form.get('search_term')
  search_results = Artist.query.filter(Artist.name.ilike("%{}%".format(searched_artist))).all()
  data = []

  for vals in search_results:
    data.append({
      "id" : vals.id,
      "name" : vals.name
    })

  response = {
    "count" : len(search_results),
    "data" : data
  }
    
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  showArtist = Artist.query.get(artist_id)
  past_shows = Shows.query.join(Artist).filter(Shows.artist_id ==Artist.id).filter(Shows.start_time<datetime.now()).all()
  upcoming_shows = Shows.query.join(Artist).filter(Shows.artist_id == Artist.id).filter(Shows.start_time>=datetime.now()).all()
  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  past_shows_list = []
  for each in past_shows:
    venueShowing = Venue.query.get(each.venue_id)
    past_shows_list.append({
      "venue_id" : each.venue_id,
      "venue_name" : venueShowing.name,
      "venue_image_link" : venueShowing.image_link,
      "start_time" : str(each.start_time)

    })

    upcoming_shows_list = []
    for each in upcoming_shows:
      venueUpcoming = Venue.query.get(each.venue_id)
      upcoming_shows_list.append({
        "venue_id" : each.venue_id,
        "venue_name" : venueUpcoming.name,
        "venue_image_link" : venueUpcoming.image_link,
        "start_time" : str(each.start_time)
      })


  data = {
    "id" : showArtist.id,
    "name" : showArtist.name,
    "genres" : showArtist.genres,
    "city" : showArtist.city,
    "state" : showArtist.state,
    "phone" : showArtist.phone,
    "website" : showArtist.website_link,
    "facebook_link" : showArtist.facebook_link,
    "image_link" : showArtist.image_link,
    "seeking_venue" : showArtist.venue_seek,
    "seeking_description" : showArtist.description,
    "past_shows" : past_shows_list,
    "upcoming_shows" : upcoming_shows_list,
    "past_shows_count" : past_shows_count,
    "upcoming_shows_count" : upcoming_shows_count
  }


  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist =Artist.query.get(artist_id)
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # # TODO: populate form with fields from artist with ID <artist_id>
  form.name.data = artist.name
  form.city.data = artist.city
  form.genres.data = artist.genres
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_description.data = artist.description
  form.seeking_venue.data = artist.venue_seek
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  if form.validate():
    error = False
    try: 
      artist_val = Artist.query.get(artist_id)
      artist_val.name = form.name.data
      artist_val.city = form.city.data
      artist_val.state = form.state.data
      artist_val.phone = form.phone.data
      artist_val.image_link = form.image_link.data
      artist_val.facebook_link = form.facebook_link.data
      artist_val.genres = form.genres.data
      artist_val.website_link = form.website_link.data
      artist_val.venue_seek = form.seeking_venue.data
      artist_val.descrption = form.seeking_description.data
      db.session.commit()
      flash("Succesful update of artist with id: " + str(artist_val.id))
    except:
      error = True
      flash("Unsuccesful update of artist with id: " + str(artist_val.id))
      db.session.rollback()
      print(sys.exc_info)
    finally:
      db.session.close()
      if error == True:
        abort(400)
  else:
    msg_error = []
    for k,v in form.errors.items():
      msg_error.append(k + " " + '|'.join(v))
    flash("Oops!!! " +str(msg_error))
  



  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # # TODO: populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.address.data = venue.address
  form.city.data = venue.city
  form.phone.data = venue.phone
  form.seeking_talent.data = venue.talent_search
  form.seeking_description.data = venue.description
  form.genres.data = venue.genres
  form.state.data = venue.state
  form.website_link.data = venue.website_link
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate():
    error_venue = False
    try:
      venue_val = Venue.query.get(venue_id)
      venue_val.name = form.name.data
      venue_val.city = form.city.data
      venue_val.state = form.state.data
      venue_val.address = form.address.data
      venue_val.phone = form.phone.data
      venue_val.image_link = form.image_link.data
      venue_val.facebook_link = form.facebook_link.data
      venue_val.genres = form.genres.data
      venue_val.website_link = form.website_link.data
      venue_val.talent_search = form.seeking_talent.data
      venue_val.description = form.seeking_description.data
      db.session.commit()
      flash("Succesful update of Venue with id: " + str(venue_val.id))
    except:
      error_venue = True
      db.session.rollback()
      print(sys.exc_info)
    finally:
      db.session.close()
      if error_venue == True:
        abort(400)
  else:
    err_msg = []
    for k,v in form.errors.items():
      err_msg.append(k +" "+ '|'.join(v))
    flash("Ooops!!! " + str(err_msg))


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()


  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  if form.validate():
    errors_in = False
    try:
      artist_add = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        genres = form.genres.data,
        website_link = form.website_link.data,
        venue_seek = form.seeking_venue.data,
        description = form.seeking_description.data
      )
      db.session.add(artist_add)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      errors_in = True
      flash('An error occurred. Artist ' + artist_add.name + ' could not be listed.')
      db.session.rollback()
      print(sys.exc_info)
    finally:
      db.session.close()
      if errors_in ==True:
        abort(400)
  
  else:
    err_message = []
    for k,v in form.errors.items():
      err_message.append(k + " " + "|".join(v))
    flash('Ooops!!! - '+ str(err_message)) 





  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows_available = Shows.query.all()
  data = []
  for available in shows_available:
    the_venue = Venue.query.get(available.venue_id)
    the_artist = Artist.query.get(available.artist_id)
    data.append({
      "venue_id" : available.venue_id,
      "venue_name" : the_venue.name,
      "artist_id" : available.artist_id,
      "artist_name" : the_artist.name,
      "artist_image_link" : the_artist.image_link,
      "start_time" : str(available.start_time)

    })

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  if form.validate():
    show_error = False
    try:
      new_show = Shows(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
      )
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      show_error= True
      print(sys.exc_info)
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
      if show_error == True:
        abort(400)
  else:
    error_message = []
    for k,v in form.errors.items():
      error_message.append(k + " " + '|'.join(v))
    flash("Ooops!!!! " + str(error_message))


  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
    app.debug = False

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
