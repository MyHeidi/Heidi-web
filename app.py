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
    message = "You arrived in London Heathrow - Need some help?"
    questions = [
        {
            "question": "What type of food?",
            "answers": [
                {
                    "answer": "mexican",
                    "action": "question",  # question, maps, uber, social, null
                    "questions": [],
                    "location": {
                        "lat": 8.2342,
                        "lng": 47.323,
                    }
                }
            ]
        }
        ]
    return jsonify(action=action, message=message, questions=questions)
