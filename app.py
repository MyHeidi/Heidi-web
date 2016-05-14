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
            "answer": "\U0001F3E8",  # Hotel
            # "action": "question",  # question, maps, uber, social, null
            "questions": [],
            "location": {
                "lat": 8.2342,
                "lng": 47.323,
            }
        }, {
            "answer": "\U0001F4DE",  # Phone
            "action": "question",  # null
            "questions": [],
            "location": {
                "lat": 8.2342,
                "lng": 47.323,
            }
        }, {
            "answer": "\U00002139",  # Information source
            "action": "question",  # question, maps, uber, social, null
            "questions": [],
        }]
    }]
    return jsonify(action=action, message=message, questions=questions)
