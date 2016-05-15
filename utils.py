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
            status = weather.get_status().lower().replace(
                'clouds', 'cloudy').replace('rain', 'rainy').replace('sun', 'sunny')
            temperature = weather.get_temperature('celsius')
            temperature_min = int(temperature['temp_min'])
            temperature_max = int(temperature['temp_max'])
            if temperature_max - temperature_min > 2:
                temperature_s = "{} to {} °C".format(temperature_min, temperature_max)
            else:
                temperature_s = str(temperature_max)
            return "It's currently {} at around {} °C.".format(status, temperature_s)
    return None


def get_weather_at_coords(weather_client, lat, lng):
    return get_weather_answer(weather_client.weather_at_coords(lat, lng))


def get_weather_at_place(weather_client, place):
    return get_weather_answer(weather_client.weather_at_place(place))
