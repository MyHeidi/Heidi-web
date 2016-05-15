from flask import request, abort


def get_lng_lat():
    lng = request.form.get('lng')
    lat = request.form.get('lat')
    try:
        return float(lng), float(lat)
    except ValueError:
        abort(400, "Missing field: lng or lat")


def get_weather_answer(observation):
    if observation:
        weather = observation.get_weather()
        if weather:
            temperature = weather.get_temperature('celsius')
            return "It's currently {} at around {} to {} °C.".format(
                weather.get_status().lower(), temperature['temp_min'], temperature['temp_max']
            )
    return None


def get_weather_at_coords(weather_client, lat, lng):
    return get_weather_answer(weather_client.weather_at_coords(lat, lng))


def get_weather_at_place(weather_client, place):
    return get_weather_answer(weather_client.weather_at_place(place))
