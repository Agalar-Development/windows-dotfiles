import requests
import os
import yaml

def get_weather_from_weatherapi():
    # Config dosyasından api_key ve location al
    config_path = os.path.expanduser(r'C:/Users/mert/.config/yasb/config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    weather_cfg = config.get('widgets', {}).get('weather', {}).get('options', {})
    api_key = weather_cfg.get('api_key')
    location = weather_cfg.get('location')
    if not api_key or api_key == 'Enter Api Key' or not location or location == 'Enter Location':
        return {'error': 'API anahtarı veya konum eksik!'}
    url = f'https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no'
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        # YASB widget'ına uygun örnek çıktı
        return {
            'temp': data['current']['temp_c'],
            'icon': data['current']['condition']['icon'],
            'location': data['location']['name'],
            'min_temp': data['current']['temp_c'],  # WeatherAPI free API'de min/max yok, sadece current var
            'max_temp': data['current']['temp_c'],
            'humidity': data['current']['humidity'],
            'desc': data['current']['condition']['text'],
        }
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print(get_weather_from_weatherapi())
