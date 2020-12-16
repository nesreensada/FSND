#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from models import *
from forms import *
import sys
from collections import defaultdict

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

	current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
	venues = Venue.query.all()
	data_dict = defaultdict(dict)
	
	for venue in venues:
		# data_dict --> key city_state
		data_dict_key = venue.city + '_' + venue.state
		# TODO: replace with real venues data.
		# num_shows should be aggregated based on number of upcoming shows per venue.
		num_upcoming_shows = venue.shows.filter(Show.start_time > current_time).count()
		venue_obj = {
					"id": venue.id,
					"name": venue.name,
					"num_upcoming_shows": num_upcoming_shows
					}
		if data_dict_key not in data_dict:
			data_dict[data_dict_key] = {
				"city": venue.city,
				"state": venue.state,
				"venues": [venue_obj]
			}
		else:
			# update the venues element only 
			data_dict[data_dict_key]['venues'].append(venue_obj)

	data = list(data_dict.values())
	return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['GET', 'POST'])
def search_venues():
	search_term = request.form.get('search_term','') 
	result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for Hop should return "The Musical Hop".
	# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
	response={
		"count": result.count(),
		"data": result.all()
	}
	return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	data = {}
	venue = Venue.query.get(venue_id)
	if venue:
		shows = Show.query.filter_by(venue_id=venue_id)
		upcoming_shows = []
		past_shows = []
		for show in shows:
			show_details = {
				"artist_id": show.artist.id,
				"artist_name": show.artist.name,
				"artist_image_link": show.artist.image_link,
				"start_time": format_datetime(str(show.start_time))
			}
			if show.start_time > current_time:
				upcoming_shows.append(show_details)
			else:
				past_shows.append(show_details)
		data = {**venue.__dict__, 
				"past_shows": past_shows,
				"upcoming_shows": upcoming_shows,
				"past_shows_count": len(past_shows),
				"upcoming_shows_count": len(upcoming_shows),
				}
	return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
	seeking_talent = False
	if seeking_talent in request.form:
		seeking_talent = request.form['seeking_talent'] == 'y'
	# TODO: insert form data as a new Venue record in the db, instead
	# TODO: modify data to be the data object returned from db insertion
	try:
		# get the data from the form    
		venue = Venue(name=request.form.get('name'),
		city=request.form.get('city'),
		state=request.form.get('state'),
		address=request.form.get('address'),
		phone=request.form.get('phone'),
		image_link=request.form.get('image_link'),
		genres=request.form.get('genres'),
		facebook_link=request.form.get('facebook_link'),
		seeking_talent_description=request.form.get('seeking_talent_description', ''),
		website=request.form.get('website'),
		seeking_talent=seeking_talent)

		db.session.add(venue)
		db.session.commit()
		# on successful db insert, flash success
		flash('Venue ' + request.form['name'] + ' was successfully listed!')

	except:
			print(sys.exc_info())
			# TODO: on unsuccessful db insert, flash an error instead.
			flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
			db.session.rollback()
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
			flash('Venue ' + venue_id + ' was successfully deleted!')
			return render_template('pages/home.html')
		except:
			print(sys.exc_info())
			flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
			db.session.rollback()
		finally:
			db.session.close()
		return render_template('pages/home.html')


	# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
	# clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	# TODO: replace with real data returned from querying the database
	data = Artist.query.all()
	return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['GET','POST'])
def search_artists():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
	# search for "band" should return "The Wild Sax Band".
	search_term = request.form.get('search_term','') 
	result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
	response={
		"count": result.count(),
		"data": result.all()
	}
	return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	data = {}
	artist = Artist.query.get(artist_id)
	if artist:
		shows = Show.query.filter_by(artist_id=artist_id)
		upcoming_shows = []
		past_shows = []
		for show in shows:
			show_details = {
				"artist_id": show.venue.id,
				"artist_name": show.venue.name,
				"artist_image_link": show.venue.image_link,
				"start_time": format_datetime(str(show.start_time))
			}
			if show.start_time > current_time:
				upcoming_shows.append(show_details)
			else:
				past_shows.append(show_details)
		data = {**artist.__dict__, 
				"past_shows": past_shows,
				"upcoming_shows": upcoming_shows,
				"past_shows_count": len(past_shows),
				"upcoming_shows_count": len(upcoming_shows),
				}
	return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	form = ArtistForm()
	artist = Artist.row2dict(Artist.query.get(artist_id))
	
	# TODO: populate form with fields from artist with ID <artist_id>
	return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	# TODO: take values from the form submitted, and update existing
	# artist record with ID <artist_id> using the new attributes
	artist_dict = Artist.row2dict(Artist.query.get(artist_id))
	try:
		artist_dict.update(request.form.to_dict())
		artist = Artist(**artist_dict)
		flash('Artist ' + request.form['name'] + ' was successfully updated!')
	except:
		print(sys.exc_info())
		# TODO: on unsuccessful db insert, flash an error instead.
		flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
		db.session.rollback()
	finally:
		db.session.close()
	# TODO: take values from the form submitted, and update existing
	# venue record with ID <venue_id> using the new attributes
	return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	
	venue = Venue.row2dict(Venue.query.get(venue_id))
	form = VenueForm()
	# TODO: populate form with values from venue with ID <venue_id>
	return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	venue_dict = Venue.row2dict(Venue.query.get(venue_id))
	try:
		venue_dict.update(request.form.to_dict())
		venue = Venue(**venue_dict)
		flash('Venue ' + request.form['name'] + ' was successfully updated!')
	except:
		print(sys.exc_info())
		# TODO: on unsuccessful db insert, flash an error instead.
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
		db.session.rollback()
	finally:
		db.session.close()
	# TODO: take values from the form submitted, and update existing
	# venue record with ID <venue_id> using the new attributes
	return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
	form = ArtistForm()
	return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
	print('do we get here', request.form.to_dict())
	seeking_venue = False
	if seeking_venue in request.form:
		seeking_venue = request.form['seeking_venue'] == 'y'
	try:
		artist = Artist(name=request.form.get('name'),
			address=request.form.get('address'),
			 city=request.form.get('city'),
			 state=request.form.get('state'),
			 phone=request.form.get('phone'),
			 image_link=request.form.get('image_link'),
			 genres=request.form.get('genres'),
			 facebook_link=request.form.get('facebook_link'),
			 seeking_venue_description=request.form.get('seeking_venue_description', ''),
			 website=request.form.get('website', ''),
			 seeking_venue=seeking_venue
		)
		# called upon submitting the new artist listing form
		# TODO: insert form data as a new Venue record in the db, instead
		# TODO: modify data to be the data object returned from db insertion
		print(Artist.row2dict(artist), 'what is here')
		db.session.add(artist)
		db.session.commit()
		# on successful db insert, flash success
		flash('Artist ' + request.form['name'] + ' was successfully listed!')
	except:
		print(sys.exc_info())
		# TODO: on unsuccessful db insert, flash an error instead.
		flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
		db.session.rollback()
	finally:
		db.session.close()
	return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
	# displays list of shows at /shows
	# TODO: replace with real venues data.
	#       num_shows should be aggregated based on number of upcoming shows per venue.
	data=[{
		"venue_id": 1,
		"venue_name": "The Musical Hop",
		"artist_id": 4,
		"artist_name": "Guns N Petals",
		"artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
		"start_time": "2019-05-21T21:30:00.000Z"
	}, {
		"venue_id": 3,
		"venue_name": "Park Square Live Music & Coffee",
		"artist_id": 5,
		"artist_name": "Matt Quevedo",
		"artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
		"start_time": "2019-06-15T23:00:00.000Z"
	}, {
		"venue_id": 3,
		"venue_name": "Park Square Live Music & Coffee",
		"artist_id": 6,
		"artist_name": "The Wild Sax Band",
		"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
		"start_time": "2035-04-01T20:00:00.000Z"
	}, {
		"venue_id": 3,
		"venue_name": "Park Square Live Music & Coffee",
		"artist_id": 6,
		"artist_name": "The Wild Sax Band",
		"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
		"start_time": "2035-04-08T20:00:00.000Z"
	}, {
		"venue_id": 3,
		"venue_name": "Park Square Live Music & Coffee",
		"artist_id": 6,
		"artist_name": "The Wild Sax Band",
		"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
		"start_time": "2035-04-15T20:00:00.000Z"
	}]
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

	# on successful db insert, flash success
	flash('Show was successfully listed!')
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
		app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
		port = int(os.environ.get('PORT', 5000))
		app.run(host='0.0.0.0', port=port)
'''
