import datetime
import json
import os
import random

import googlemaps
from apns import APNs, Payload
from flask import Flask, request, jsonify, render_template, abort
from flask.ext.socketio import SocketIO
from flask.ext.uploads import configure_uploads
from havenondemand.hodclient import HODClient, HODApps
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

import settings
from extensions import db, debug_toolbar, photos
from utils import get_lng_lat

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
    #print(maps_client.places_nearby((-33.86746, 151.207090)))
    socket_io.emit('log', {'lng': lng, 'lat': lat})
    action = "notification"
    message = "You arrived at London Gatwick Airport"
    return jsonify(action=action, message=message)


@app.route('/get_question', methods=['POST'])
def get_question():
    lng, lat = get_lng_lat()
    prev_answers = json.loads(request.form.get('prev_answers', '[]'))
    socket_io.emit('log', {'lng': lng, 'lat': lat, 'prev_answers': prev_answers})
    action = None
    id = None
    question = None
    answers = None
    question_ids = list(map(lambda answer: answer['question_id'], prev_answers))
    answer_ids = list(map(lambda answer: answer['answer_id'], prev_answers))
    if len(question_ids) == 0:
        if lat == 51.153662 and lng == -0.182063:
            action = 'question'
            id = 'q_airport'
            question = "You arrived at London Gatwick Airport. Do you need some assistance?"
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
        else:
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
                'url': 'http://dev.heidi.wx.rs/action/phone_charges/go_europe',
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
                    }, {
                        'id': 'a_leisure_restaurants_distance_10',
                        'answer': 'leisure_restaurants_distance_10',
                        'action': 'request',
                    }, {
                        'id': 'a_leisure_restaurants_distance_30',
                        'answer': 'leisure_restaurants_distance_30',
                        'action': 'request',
                    }]
            elif answer_ids[0] == 'a_leisure_bars':
                # TODO
                pass
            elif answer_ids[0] == 'a_leisure_clubs':
                # TODO
                pass
        else:
            abort(500, "Unknown previous question")
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
    if face:
        photo_type = 'selfie'
        photo_info = {'face': face}
    return jsonify(type=photo_type, info=photo_info, id=None)


@app.route('/apn/<notification>')
def send_apn(notification):
    payload = Payload(content_available=True)
    payload_alert = Payload(alert="test")
    results = []
    for token in app.config.get('APN_TOKENS'):
        results.append(apn_client.gateway_server.send_notification(token, payload, random.getrandbits(32)))
        #results.append(apn_client.gateway_server.send_notification(token, payload_alert, random.getrandbits(32)))
    return jsonify(results=results)


@app.route('/apn_feedback')
def get_apn_feedback():
    errors = []
    for token, fail_time in apn_client.feedback_server.items():
        errors.append({'token': token, 'time': fail_time})
    return repr(errors)


@socket_io.on('my event')
def handle_my_custom_event(data):
    print('received json: ' + str(data))


if __name__ == '__main__':
    socket_io.run(app)
