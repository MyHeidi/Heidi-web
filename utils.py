from flask import request, abort


def get_lng_lat():
    lng = request.form.get('lng')
    lat = request.form.get('lat')
    if lng is None or lat is None:
        abort(400, "Missing field: lng or lat")
    return lng, lat
