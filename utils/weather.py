import requests

async def get_weather_by_city(city_name):
    api_key = "7624baa6d18e6ba45825a7d701414994"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?q={city_name}&appid={api_key}&units=metric&lang=ru"
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] not in ["401","404"]:
        icon_id = data["weather"][0]["icon"]
        icon_url = f'http://openweathermap.org/img/wn/{icon_id}@4x.png'
        main = data["main"]
        temperature = main["temp"]
        wind = data["wind"]["speed"]
        city = data["name"]
        weather_description = data["weather"][0]["description"]
        weather_string = f"Город: {city}\nТемпература: {round(temperature)}°C\nСкорость ветра: {round(wind)} м/c\n{weather_description.capitalize()}"
        return [weather_string, icon_url]
    else:
        return ["Город не найден, пожалуйста, проверьте название и попробуйте снова.", 0]

async def get_weather_by_coords(coord_string):
    api_key = "7624baa6d18e6ba45825a7d701414994"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    coords = coord_string.split(",")
    complete_url = f"{base_url}?lat={coords[0]}&lon={coords[1]}&appid={api_key}&units=metric&lang=ru"
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] not in ["401","404"]:
        icon_id = data["weather"][0]["icon"]
        icon_url = f'http://openweathermap.org/img/wn/{icon_id}@4x.png'
        main = data["main"]
        temperature = main["temp"]
        wind = data["wind"]["speed"]
        city_name = data["name"]
        weather_description = data["weather"][0]["description"]
        weather_string = f"Город: {city_name}\nТемпература: {round(temperature)}°C\nСкорость ветра: {round(wind)} м/c\n{weather_description.capitalize()}"
        return [weather_string, icon_url]
    else:
        return ["Не удалось получить погоду для данной локации.", 0]
    
