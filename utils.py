from flask import request, abort


def get_lng_lat():
    lng = request.form.get('lng')
    lat = request.form.get('lat')
    try:
        return float(lng), float(lat)
    except ValueError:
        abort(400, "Missing field: lng or lat")


def get_weather(weather_client, lat, lng):
    observation = weather_client.weather_around_coords(lat, lng)
    if observation:
        weather = observation[0].get_weather()
        if weather:
            temperature = weather.get_temperature('celsius')
            return "It's currently {} at around {} to {} °C.".format(
                weather.get_status().lower(), temperature['temp_min'], temperature['temp_max']
            )
    return None
