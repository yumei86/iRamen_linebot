import requests
import json
#--------------------天氣weather api--------------------------------
def query_local_weather(lon,lat,APIkey,whole_store):
    weather_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,daily&lang=zh_tw&appid={APIkey}&units=metric'
    get_weather_data = requests.get(weather_url)
    weather_data  = get_weather_data.json()
    weather_description = weather_data['current']['weather'][0]['description']
    main_temp = weather_data['current']['temp']
    temp_feels_like = weather_data['current']['feels_like']
    humidity_procent = weather_data['current']['humidity']
    uvi_index = weather_data['current']['uvi']
    uvi_index_description = ''
    if 0 <= uvi_index <= 2:
      uvi_index_description = '對於一般人無危險'
    elif 3 <= uvi_index <= 5:
      uvi_index_description = '無保護暴露於陽光中有較輕傷害的風險'
    elif 6 <= uvi_index <= 7:
      uvi_index_description = '無保護暴露於陽光中有很大傷害的風險'
    elif 8 <= uvi_index <= 10:
      uvi_index_description = '暴露於陽光中有極高風險'
    elif 11 <= uvi_index:
      uvi_index_description = '暴露於陽光中極其危險'
    else:
      uvi_index_description = '目前無相關資訊'
    weather_result = f'目前{whole_store}\n\n【{weather_description}】\n\n氣溫:{main_temp}℃\n體感溫度:{temp_feels_like}℃\n濕度:{humidity_procent}%\n紫外線指數:{uvi_index}，{uvi_index_description}'
    return weather_result