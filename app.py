from flask import Flask, request, jsonify

import settings
from extensions import db, debug_toolbar

app = Flask(__name__)
app.config.from_object(settings)
db.init_app(app)
debug_toolbar.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    return "done"


@app.route('/update_location', methods=['GET', 'POST'])
def updateLocation():
    if request.method == 'POST':
        lng = request.form.get('lng')
        lat = request.form.get('lat')
    else:
        lng = 0
        lat = 0
    print("Data: lng: {}, lat: {}".format(lng, lat))
    action = "notification"
    message = "You arrived at London Gatwick Airport"
    return jsonify(action=action, message=message)


@app.route('/get_question')
def get_question():
    if request.method == 'POST':
        lng = request.form.get('lng', 0)
        lat = request.form.get('lat', 0)
        prev_answers = request.form.get('prev_answers')
    else:
        lng = 0
        lat = 0
        prev_answers = []
    action = "question"
    id = "q_airport"
    question = "You arrived at London Gatwick Airport. Do you need some assistance?",
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
    }],
    """"questions": [{
            "question": "Roaming charges (CHF):\nTo CH: 2.- per min\nLocal: 1.20 per min\nIncomming: 1.- per min\nSMS: 0.45\nData: 2.- per MB\nActivate Go Europe?",
            "answers": [{
                "answer": "yes",
                "action": "request",
                "url": "http://dev.heidi.wx.rs/action/phone_charges/go_europe",
            }, {
                "answer": "no",
                "action": None,
            }],
        }],"""

    return jsonify(action=action, id=id, question=question, answers=answers)
