#----------------------------------------------------------------------------#
# Imports.
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for,
  jsonify
  )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import (
  Formatter,
  FileHandler
  )
from flask_wtf import Form
from forms import *
from forms import VenueForm
from flask_migrate import Migrate
from models import (
  app,
  db,
  Venue,
  Artist,
  Show
)

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  data = []
  venues = Venue.query.all()
  for location in Venue.query.with_entities(Venue.city, Venue.state).distinct():
    data.append({
      "city": location.city,
      "state": location.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name
      } for venue in venues if
            venue.city == location.city and venue.state == location.state
      ]})
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implements search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  word = request.form.get('search_term').lower()
  response = {}
  data = []
  for venue in Venue.query.all():
    details = {
      "id": venue.id,
      "name": venue.name,
    }
    if word in venue.name.lower():
      data.append(details)
  response['count'] = len(data)
  response['data'] = data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replaces with real venue data from the venues table, using venue_id
  present = datetime.now()
  pastshows = []
  upcomingshows = []
  shows = Show.query.filter_by(venue_id=venue_id).join(Artist)
  for show in shows:
    details = [{
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      }]
    if show.start_time < present:
      pastshows.extend(details)
    else:
      upcomingshows.extend(details)
  data = Venue.query.get(venue_id).__dict__
  data['past_shows'] = pastshows
  data['upcoming_shows'] = upcomingshows
  data['past_shows_count'] = len(pastshows)
  data['upcoming_shows_count'] = len(upcomingshows)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # inserts form data as a new Venue record in the db, instead
  # modifies data to be the data object returned from db insertion
  form = VenueForm()
  try:
    venue = Venue(
      name=form.name.data,
      genres=form.genres.data,
      address=form.address.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      website=form.website.data,
      facebook_link=form.facebook_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data,
      image_link=form.image_link.data,
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash(venue.name +  ' has been successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    db.session.close()
    return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replaces with real data returned from querying the database
  data = []
  for artist in Artist.query.all():
    details = {
        "id": artist.id,
        "name": artist.name,
    }
    data.append(details)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implements search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  word = request.form.get('search_term').lower()
  response = {}
  data = []
  for artist in Artist.query.all():
    details = {
      "id": artist.id,
      "name": artist.name,
    }
    if word in artist.name.lower():
      data.append(details)
  response['count'] = len(data)
  response['data'] = data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # replaces with real venue data from the venues table, using venue_id
  present = datetime.now()
  pastshows = []
  upcomingshows = []
  for show in Show.query.filter_by(artist_id=artist_id):
    venue = Venue.query.get(show.venue_id)
    details = [{
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time)
      }]
    if show.start_time < present:
      pastshows.extend(details)
    else:
      upcomingshows.extend(details)
  data = Artist.query.get(artist_id).__dict__
  data['past_shows'] = pastshows
  data['upcoming_shows'] = upcomingshows
  data['past_shows_count'] = len(pastshows)
  data['upcoming_shows_count'] = len(upcomingshows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # populates form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # takes values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  try:
    artist = Artist.query.get(artist_id)
    artist.name=form.name.data,
    artist.genres=form.genres.data,
    artist.city=form.city.data,
    artist.state=form.state.data,
    artist.phone=form.phone.data,
    artist.website=form.website.data,
    artist.facebook_link=form.facebook_link.data,
    # seeking_talent=form.seeking_talent.data,
    artist.image_link=form.image_link.data,
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be edited.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # populates form with values from venue with ID <venue_id>
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # takes values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    venue.name=form.name.data,
    venue.genres=form.genres.data,
    venue.address=form.address.data,
    venue.city=form.city.data,
    venue.state=form.state.data,
    venue.phone=form.phone.data,
    venue.website=form.website.data,
    venue.facebook_link=form.facebook_link.data,
    # venue.seeking_talent=form.seeking_talent.data,
    # venue.seeking_description=form.seeking_description.data,
    venue.image_link=form.image_link.data,
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. venue ' + form.name.data + ' could not be edited.')
  finally:
    db.session.close()
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
  # inserts form data as a new Venue record in the db, instead
  # modifies data to be the data object returned from db insertion
  form = ArtistForm()
  try:
    artist = Artist(
      name=form.name.data,
      genres=form.genres.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      website=form.website.data,
      facebook_link=form.facebook_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data,
      image_link=form.image_link.data,
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash(artist.name +  ' has been successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be deleted.')
  finally:
    db.session.close()
    return jsonify({'success': True})

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shwows at /shows
  artists = Artist.query.all()
  venues = Venue.query.all()
  data = []
  for show in Show.query.all():
    artist = [artist for artist in artists if artist.id == show.artist_id][0]
    venue = [venue for venue in venues if venue.id == show.venue_id][0]
    details = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
      }
    data.append(details)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # inserts form data as a new Show record in the db
  form = ShowForm()
  try:
    show = Show(
      venue_id=form.venue_id.data,
      artist_id=form.artist_id.data,
      start_time=form.start_time.data,
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
