import json

from flask import Flask, request, jsonify
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

import settings
from extensions import db, debug_toolbar

app = Flask(__name__)
app.config.from_object(settings)
db.init_app(app)
debug_toolbar.init_app(app)

yelp_client = Client(Oauth1Authenticator(
    consumer_key=app.config.get('YELP_CONSUMER_KEY'),
    consumer_secret=app.config.get('YELP_CONSUMER_SECRET'),
    token=app.config.get('YELP_TOKEN'),
    token_secret=app.config.get('YELP_TOKEN_SECRET')
))


@app.route('/', methods=['GET', 'POST'])
def home():
    return "done"


@app.route('/update_location', methods=['POST'])
def updateLocation():
    lng = request.form.get('lng')
    lat = request.form.get('lat')

    print("Data: lng: {}, lat: {}".format(lng, lat))

    action = "notification"
    message = "You arrived at London Gatwick Airport"
    return jsonify(action=action, message=message)


@app.route('/get_question', methods=['POST'])
def get_question():
    lng = request.form.get('lng', 0)
    lat = request.form.get('lat', 0)
    prev_answers = json.loads(request.form.get('prev_answers', '[]'))

    print("Data: lng: {}, lat: {}, prev_answers: {}".format(lng, lat, prev_answers))

    action = None
    id = None
    question = None
    answers = None
    if len(prev_answers) == 0:  # TODO: Check location for Gatwick
        action = "question"
        id = "q_airport"
        question = "You arrived at London Gatwick Airport. Do you need some assistance?"
        answers = [{
            "id": "a_airport_hotel_route",
            "answer": "hotel_route",  # Hotel
            "action": "route",
            "location": {
                "lat": -0.07034167,
                "lng": 51.510425,
            }
        }, {
            "id": "a_airport_phone_charges",
            "answer": "phone_charges",  # Phone
            "action": "question",  # null
        }, {
            "id": "a_airport_country_info",
            "answer": "country_info",  # Phone
            "action": "url",  # null
            "url": "https://en.wikipedia.org/wiki/Gatwick_Airport",
        }]
    elif len(prev_answers) == 1:
        if prev_answers[0]['question_id'] == "q_airport":
            action = "question"
            id = "q_airport_roaming"
            question = "Roaming charges (CHF):\nTo CH: 2.- per min\nLocal: 1.20 per min\nIncomming: 1.- per min\nSMS: 0.45\nData: 2.- per MB\nActivate Go Europe?"
            answers = [{
                "answer": "yes",
                "action": "request",
                "url": "http://dev.heidi.wx.rs/action/phone_charges/go_europe",
            }, {
                "answer": "no",
                "action": None,
            }]
        else:
            print("Unknown previous question")
    else:
        print("Unknown previous answers")

    if action is None:
        return jsonify(action=None)
    print(question)
    return jsonify(action=action, id=id, question=question, answers=answers)


@app.route('/local/restaurants', methods=['POST'])
def local_restaurants():
    lng = request.form.get('lng', 0)
    lat = request.form.get('lat', 0)
    params = {
        'category_filter': 'food',
        'term': 'italian',
    }
    result = yelp_client.search_by_coordinates(lat, lng, **params)
    print(result)
    return str(result)


@app.route('/local/bars', methods=['POST'])
def local_bars():
    lng = request.form.get('lng', 0)
    lat = request.form.get('lat', 0)


@app.route('/local/clubs', methods=['POST'])
def local_clubs():
    lng = request.form.get('lng', 0)
    lat = request.form.get('lat', 0)


@app.route('/photo', methods=['POST'])
def upload_photo():
    lng = request.form.get('lng', 0)
    lat = request.form.get('lat', 0)
