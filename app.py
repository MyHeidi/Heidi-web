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


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        lng = request.form.get('lng')
        lat = request.form.get('lat')
    else:
        lng = 0
        lat = 0
    print("Data: lng: {}, lat: {}".format(lng, lat))
    action = "notification"
    message = "You arrived at London Gatwick Airport"
    questions = [{
        "question": "You arrived at London Gatwick Airport. Do you need some assistance?",
        "answers": [{
            "answer": "hotel_route",  # Hotel
            "action": "route",  # question, maps, uber, social, null
            "location": {
                "lat": -0.07034167,
                "lng": 51.510425,
            }
        }, {
            "answer": "phone_charges",  # Phone
            "action": "question",  # null
            "question": {
                "question": "Roaming charges (CHF):\nTo CH: 2.- per min\nLocal: 1.20 per min\nIncomming: 1.- per min\nSMS: 0.45\nData: 2.- per MB\nActivate Go Europe?",
                "answers": [{
                    "answer": "yes",
                    "action": "request",
                    "url": "http://dev.heidi.wx.rs/action/phone_charges/go_europe",
                }, {
                    "answer": "no",
                    "action": None,
                }],
            }
        }, {
            "answer": "country_info",  # Phone
            "action": "url",  # null
            "url": "https://en.wikipedia.org/wiki/Gatwick_Airport",
        }],
    }]
    return jsonify(action=action, message=message, questions=questions)
