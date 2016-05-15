import datetime
import json
import os
import random

import googlemaps
import pyowm as pyowm
import re

import twitter

from apns import APNs, Payload
from flask import Flask, request, jsonify, render_template, abort, url_for
from flask.ext.socketio import SocketIO
from flask.ext.uploads import configure_uploads
from havenondemand.hodclient import HODClient, HODApps
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

import settings
from extensions import db, debug_toolbar, photos
from utils import get_lng_lat, get_weather_at_coords, get_weather_at_place

app = Flask(__name__)
app.config.from_object(settings)
db.init_app(app)
debug_toolbar.init_app(app)
configure_uploads(app, photos)

apn_client = APNs(cert_file=app.config.get('APN_CERT_PATH'), key_file=app.config.get('APN_KEY_PATH'), enhanced=True)
apn_client.gateway_server.register_response_listener(lambda err: print("APN response error: {}".format(err)))

maps_client = googlemaps.Client(key=app.config.get('GOOGLE_MAPS_API_KEY'))

yelp_client = Client(Oauth1Authenticator(
    consumer_key=app.config.get('YELP_CONSUMER_KEY'),
    consumer_secret=app.config.get('YELP_CONSUMER_SECRET'),
    token=app.config.get('YELP_TOKEN'),
    token_secret=app.config.get('YELP_TOKEN_SECRET')
))

hod_client = HODClient(app.config.get('HOD_API_KEY'), version="v1")

weather_client = pyowm.OWM(app.config.get('OPEN_WEATHER_MAP_API_KEY'))

twitter_client = twitter.Api(
    consumer_key=app.config.get('TWITTER_CONSUMER_KEY'),
    consumer_secret=app.config.get('TWITTER_CONSUMER_SECRET'),
    access_token_key=app.config.get('TWITTER_TOKEN'),
    access_token_secret=app.config.get('TWITTER_TOKEN_SECRET'))

socket_io = SocketIO(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/log', methods=['GET', 'POST'])
def log():
    return render_template('log.html')


@app.route('/update_location', methods=['POST'])
def update_location():
    lng, lat = get_lng_lat()

    # Get nearby places
    results = maps_client.places_nearby((lat, lng), radius=500, type='point_of_interest').get('results', [])

    socket_io.emit('update_location', {'lng': lng, 'lat': lat, 'results': results})

    for result in results:
        if result.get('name') == 'Gatwick Airport':
            action = "notification"
            message = "You arrived at London Gatwick Airport"
            return jsonify(action=action, message=message)

    return jsonify(action=None)


@app.route('/get_question', methods=['POST'])
def get_question():
    lng, lat = get_lng_lat()
    prev_answers = json.loads(request.form.get('prev_answers', '[]'))

    socket_io.emit('get_question', {'lng': lng, 'lat': lat, 'prev_answers': prev_answers})

    question_ids = list(map(lambda answer: answer['question_id'], prev_answers))
    answer_ids = list(map(lambda answer: answer['answer_id'], prev_answers))
    if len(question_ids) == 0:
        # Get nearby places
        results = maps_client.places_nearby((lat, lng), radius=500, type='point_of_interest').get('results', [])
        action = None
        for result in results:
            if result.get('name') == 'Gatwick Airport':
                action = 'question'
                id = 'q_airport'

                weather = get_weather_at_coords(weather_client, lat, lng)
                question = "You arrived at London Gatwick Airport.{} Do you need some assistance?".format(
                    " " + weather if weather else ""
                )
                answers = [{
                    'id': 'a_airport_hotel_route',
                    'answer': 'hotel_route',
                    'action': 'route',
                    'location': {
                        "lng": -0.07034167,
                        "lat": 51.510425,
                    }
                }, {
                    'id': 'a_airport_phone_charges',
                    'answer': 'phone_charges',
                    'action': 'question',
                }, {
                    'id': 'a_airport_country_info',
                    'answer': 'country_info',
                    'action': 'url',
                    'url': 'https://en.wikipedia.org/wiki/Gatwick_Airport',
                }]
        if action is None:
            dt = datetime.datetime.now()
            action = 'question'
            id = 'q_leisure'
            question = "It's {}. What can I help you with?".format(dt.strftime('%H:%M'))
            answers = [{
                'id': 'a_leisure_restaurants',
                'answer': 'leisure_restaurants',
                'action': 'question',
            }, {
                'id': 'a_leisure_bars',
                'answer': 'leisure_bars',
                'action': 'question',
            }, {
                'id': 'a_leisure_clubs',
                'answer': 'leisure_clubs',
                'action': 'question',
            }]
    else:
        if question_ids[0] == 'q_airport':
            action = 'question'
            id = 'q_airport_roaming'
            question = "Roaming charges (CHF):\nTo CH: 2.- per min\nLocal: 1.20 per min\nIncomming: 1.- per min\nSMS: 0.45\nData: 2.- per MB\nActivate Go Europe?"
            answers = [{
                'id': 'a_airport_roaming_yes',
                'answer': 'airport_roaming_yes',
                'action': 'request',
                'url': url_for('action_phone_charges', action='go_europe'),
            }, {
                'id': 'a_airport_roaming_no',
                'answer': 'airport_roaming_no',
                'action': None,
            }]
        elif question_ids[0] == 'q_leisure':
            if answer_ids[0] == 'a_leisure_restaurants':
                if len(question_ids) == 1:
                    action = 'question'
                    id = 'q_leisure_restaurants_cuisine'
                    question = "What kind of cuisine would you prefer?"
                    answers = [{
                        'id': 'a_leisure_restaurants_cuisine_italian',
                        'answer': 'leisure_restaurants_cuisine_italian',
                        'action': 'question',
                    }, {
                        'id': 'a_leisure_restaurants_cuisine_indian',
                        'answer': 'leisure_restaurants_cuisine_indian',
                        'action': 'question',
                    }, {
                        'id': 'a_leisure_restaurants_cuisine_fastfood',
                        'answer': 'leisure_restaurants_cuisine_fastfood',
                        'action': 'question',
                    }]
                elif len(question_ids) == 2:
                    action = 'question'
                    id = 'q_leisure_restaurants_distance'
                    question = "How long do you want to spend to get there?"
                    answers = [{
                        'id': 'a_leisure_restaurants_distance_5',
                        'answer': 'leisure_restaurants_distance_5',
                        'action': 'request',
                        'url': url_for('action_places'),
                    }, {
                        'id': 'a_leisure_restaurants_distance_10',
                        'answer': 'leisure_restaurants_distance_10',
                        'action': 'request',
                        'url': url_for('action_places'),
                    }, {
                        'id': 'a_leisure_restaurants_distance_30',
                        'answer': 'leisure_restaurants_distance_30',
                        'action': 'request',
                        'url': url_for('action_places'),
                    }]
                else:
                    return abort(400, "No more questions to ask for restaurant")
            elif answer_ids[0] == 'a_leisure_bars':
                action = 'question'
                id = 'q_leisure_restaurants_distance'
                question = "How long do you want to spend to get there?"
                answers = None
                pass
            elif answer_ids[0] == 'a_leisure_clubs':
                action = 'question'
                id = 'q_leisure_restaurants_distance'
                question = "How long do you want to spend to get there?"
                answers = None
            else:
                return abort(500, "Unknown leisure category")
        else:
            return abort(500, "Unknown previous question")
    return jsonify(action=action, id=id, question=question, answers=answers)


@app.route('/suggestions/<category>', methods=['POST'])
def get_suggestions(category='restaurants'):
    if category not in app.config.get('SUGGESTION_CATEGORIES'):
        abort(400, "Invalid field: category {} is not supported (supported: {})".format(
            category,
            ', '.join(app.config.get('SUGGESTION_CATEGORIES'))
        ))
    lng, lat = get_lng_lat()
    if 'terms' not in request.form:
        abort(400, "Missing field: terms")
    terms = ','.join(filter(lambda term: term in app.config.get('SUGGESTION_TERMS', ()), request.form.get('terms', [])))
    results = yelp_client.search_by_coordinates(lat, lng, category_filter=category, term=terms)
    businesses = filter(lambda b: not b.is_closed, results.businesses)
    suggestions = []
    for business in businesses:
        suggestions.append({
            'id': business.id,
            'name': business.name,
            'distance': business.distance,
            'rating': business.rating,
            'image_url': business.image_url,
            'lat': business.location.coordinate.latitude,
            'lng': business.location.coordinate.longitude,
            'address': "\n".join(business.location.address),
        })
    return jsonify(suggestions=suggestions)


@app.route('/upload/photo', methods=['POST'])
def upload_photo():
    lng, lat = get_lng_lat()
    if 'photo' not in request.files:
        abort(400, "Missing field: photo")
    photo_name = photos.save(request.files['photo'])
    photo_path = os.path.join(app.config.get('UPLOADS_PHOTOS_DEST', ''), photo_name)
    response = hod_client.post_request({'file': photo_path}, HODApps.DETECT_FACES, async=False)
    photo_type = None
    photo_info = None
    face = response.get('face', [])
    action = 'question'
    if face:
        photo_type = 'selfie'
        photo_info = {'face': face}
        id = 'q_photo_share_selfie'
        question = "Do you want to share the selfie you took on Twitter?"
        answers = [{
            'id': 'a_photo_share_selfie_yes',
            'answer': 'photo_share_selfie_yes',
            'action': 'request',
            'url': url_for('action_twitter'),
            'photo': photo_name,
        }, {
            'id': 'a_photo_share_selfie_no',
            'answer': 'photo_share_selfie_no',
            'action': None,
        }]
    else:
        photo_type = 'photo'
        photo_info = {}
        id = 'q_photo_share_photo'
        question = "Would you like to share this photo on Twitter?"
        answers = [{
            'id': 'a_photo_share_photo_yes',
            'answer': 'photo_share_photo_yes',
            'action': 'request',
            'url': url_for('action_twitter'),
            'photo': photo_name,
        }, {
            'id': 'a_photo_share_photo_no',
            'answer': 'photo_share_photo_no',
            'action': None,
        }]
    return jsonify(action=action, id=id, question=question, answers=answers, type=photo_type, info=photo_info)


@app.route('/ask_question', methods=['POST'])
def ask_question():
    lng, lat = get_lng_lat()
    question = request.form.get('question')
    if not question:
        abort(400, "Missing field: question")
    response = hod_client.post_request({'text': question, 'stemming': False}, HODApps.TOKENIZE_TEXT, async=False)
    terms = response.get('terms')
    action = None

    data = {}
    for term in terms:
        if term.get('weight', 0) < 30:
            break
        term_s = re.sub(r'[^A-Z]', '', term.get('term'))
        if term_s == "WEATHER" or term_s == "TEMPERATURE":
            action = 'weather'
        elif term_s in ("RESTAURANT", "RESTAURANTS", "EAT"):
            action = 'restaurants'
        elif term_s in ("BAR", "BARS", "DRINK", "DRINKS", "PUB", "PUBS", "DRUNK", "SMASHED"):
            action = 'bars'
        elif term_s in ("CLUB", "CLUBS", "PARTY", "PARTIES"):
            action = 'clubs'
        elif term_s in ("ZURICH", "LONDON", "BERN", "BERLIN", "BRIGHTON"):
            data['place'] = term_s.lower()
    answer = "I'm sorry, I could not understand you."
    if action == 'weather' and 'place' in data:
        answer = get_weather_at_place(weather_client, data['place'])
    elif action in ('restaurants', 'bars', 'clubs'):
        pass  # TODO
    return jsonify(action='answer', answer=answer)


@app.route('/action/places', methods=['POST'])
def action_places():
    lng, lat = get_lng_lat()
    prev_answers = json.loads(request.form.get('prev_answers', '[]'))
    socket_io.emit('log', {'lng': lng, 'lat': lat, 'prev_answers': prev_answers})

    question_ids = list(map(lambda answer: answer['question_id'], prev_answers))
    answer_ids = list(map(lambda answer: answer['answer_id'], prev_answers))

    if len(question_ids) == 3 and question_ids[0] == 'q_leisure' and answer_ids[0] == 'a_leisure_restaurants':
        # Restaurants
        category = 'restaurants'
        term = answer_ids[1].replace('a_leisure_restaurants_cuisine_', '')
        distance = answer_ids[2].replace('a_leisure_restaurants_distance_', '')
    elif len(question_ids) == 3:
        # Bars
        category = 'bars'
        distance = '5'
        term = ''
    else:
        return abort(400, "Not enough information to suggest places")

    if distance == '5':
        radius = 500
    elif distance == '10':
        radius = 1000
    elif distance == '30':
        radius = 10000
    else:
        radius = 40000

    results = yelp_client.search_by_coordinates(lat, lng, radius_filter=radius, category_filter=category, term=term)
    businesses = filter(lambda b: not b.is_closed, results.businesses)
    places = []
    for business in businesses:
        places.append({
            'id': business.id,
            'name': business.name,
            'image_url': business.image_url,
            'snippet_text': business.snippet_text,
            'distance': business.distance,
            'rating': business.rating,
            'review_count': business.review_count,
            'lat': business.location.coordinate.latitude,
            'lng': business.location.coordinate.longitude,
            'address': "\n".join(business.location.display_address),
        })
    return jsonify(places=places)


@app.route('/action/phone_charges/<action>', methods=['POST'])
def action_phone_charges(action):
    return jsonify(action='answer', answer="GO Europe activated! New roaming roaming charges:\nTo CH: 1.- per min\nLocal: 0.40 per min\nIncomming: 0.- per min\nSMS: 0.20\nData: 0.10.- per MB with 1000 MB included.")


@app.route('/action/twitter', methods=['POST'])
def action_twitter():
    lng, lat = get_lng_lat()
    status = request.form.get('status')
    if 'photo' in request.files:
        photo_name = photos.save(request.files['photo'])
    else:
        photo_name = request.form.get('photo')
    if photo_name:
        photo_path = os.path.join(app.config.get('UPLOADS_PHOTOS_DEST', ''), photo_name)
        if not os.path.exists(photo_path):
            photo_path = None
    else:
        photo_path = None
    if not status:
        abort(400, "Missing field: status")
    try:
        twitter_client.PostUpdate(status, media=photo_path, latitude=lat, longitude=lng, display_coordinates=True)
        answer = "Tweeted!"
    except twitter.error.TwitterError as e:
        answer = "Could not post tweet! The API gave me this error message: \"{}\"!".format(e.message)
    return jsonify(action='answer', answer=answer)


@app.route('/apn/<notification>')
def send_apn(notification):
    payload = Payload(custom={'notification': notification}, content_available=True)
    # payload_alert = Payload(alert="test")
    results = []
    for token in app.config.get('APN_TOKENS'):
        results.append(apn_client.gateway_server.send_notification(token, payload, random.getrandbits(32)))
        # results.append(apn_client.gateway_server.send_notification(token, payload_alert, random.getrandbits(32)))
    return jsonify(results=results)


@app.route('/apn_feedback')
def get_apn_feedback():
    errors = []
    for token, fail_time in apn_client.feedback_server.items():
        errors.append({'token': token, 'time': fail_time})
    return repr(errors)


if __name__ == '__main__':
    socket_io.run(app)
