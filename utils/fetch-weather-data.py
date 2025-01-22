import csv
import datetime
import requests

API_KEY = "<secret>"
BASE_URL = "https://api.weather.com/v1/location/KBUR:9:US/observations/historical.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.wunderground.com/",
    "Origin": "https://www.wunderground.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Connection": "keep-alive",
}
CSV_COLUMNS = [
    "timestamp",
    "temperature",
    "clouds",
    "wx_phrase",
    "pressure",
    "windspeed",
    "precipitation",
    "felt_temperature",
]


def get_monthly_weather_data(api_key, start_date, end_date):
    current_date = start_date
    all_data = []

    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        start_date_str = f"{year}{month:02d}01"
        end_date_str = (current_date + datetime.timedelta(days=31)
                        ).replace(day=1) - datetime.timedelta(days=1)
        end_date_str = end_date_str.strftime("%Y%m%d")

        params = {
            "apiKey": api_key,
            "units": "m",
            "startDate": start_date_str,
            "endDate": end_date_str,
        }

        print(f"Fetching data for {start_date_str} to {end_date_str}...")
        response = requests.get(BASE_URL, headers=HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            observations = data.get("observations", [])
            for obs in observations:
                record = {
                    "timestamp": datetime.datetime.fromtimestamp(obs["valid_time_gmt"], datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
                    "temperature": obs.get("temp"),
                    "clouds": obs.get("clds"),
                    "wx_phrase": obs.get("wx_phrase"),
                    "pressure": obs.get("pressure"),
                    "windspeed": obs.get("wspd"),
                    "precipitation": obs.get("precip_hrly"),
                    "felt_temperature": obs.get("feels_like"),
                }
                all_data.append(record)
        else:
            print(f"Failed to fetch data for {start_date_str} to {
                end_date_str}: {response.status_code}")

        current_date = (
            current_date + datetime.timedelta(days=31)).replace(day=1)

    return all_data


def save_to_csv(data, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    start_date = datetime.date(2018, 1, 1)
    end_date = datetime.date(2021, 1, 1)
    weather_data = get_monthly_weather_data(API_KEY, start_date, end_date)
    output_filename = "../resources/burbank_weather_data.csv"
    save_to_csv(weather_data, output_filename)
    print(f"Data saved to {output_filename}.")
