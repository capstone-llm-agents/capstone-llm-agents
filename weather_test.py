import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from pytz import timezone
from tzlocal import get_localzone
from datetime import datetime

########llm agent setup########
llm_config = {
    "api_type": "ollama",
    "model": "gemma3",
}

weather_agent = ConversableAgent(
    name="weather_agent",
    system_message="""Your Job is to assist the user with their tasks.
    """,
    llm_config=llm_config,
    human_input_mode="NEVER",
)
########llm agent setup########

def obtain_weather_details(prompt):
    try:
        current_date = datetime.now().date()

        agent_prompt = f"""
        Break down the following tasks into the latitude and longitude of the given location as well as the date range you would expect to find the weather information.

        Tasks: {prompt}
        Current Date: {current_date}

        If no date is given assume the date is today for both the beginning and the end dates otherwise deduce the required date range.
        Directly and only answer with the follow format:
        Latitude: -10.6531
        Longitude: 14.2315
        Start date: 2025-02-27
        End date: 2025-02-28
        """

        extracted_details = weather_agent.generate_reply(messages=[{"role": "user", "content": agent_prompt}])
        print("#####################################")
        print("Extracted location and date")
        print("#####################################")
        print(extracted_details["content"])

        for line in extracted_details["content"].splitlines():
            if "Latitude:" in line:
                latitude = line.split(": ")[1].strip()
            elif "Longitude:" in line:
                longitude = line.split(": ")[1].strip()
            elif "Start date:" in line:
                start_date = line.split(": ")[1].strip()
            elif "End date:" in line:
                end_date = line.split(": ")[1].strip()

        print("\n\n\n")
        print("#####################################")
        print("Generated weather data")
        print("#####################################")
        weather_data = generate_weather_data(latitude, longitude, start_date, end_date)
        print(weather_data)
        print("\n\n\n")

        result = deduce_weather_result(prompt, weather_data)
        #print(result)
    except:
        result = "An error has occurred. make sure the date range is no more than 16 days past today. If this is not the issue than it will likely be somewhere in the system"#temporary error catching

    return result



def generate_weather_data(latitude, longitude, start_date, end_date):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "uv_index", "precipitation_probability", "precipitation", "wind_speed_10m", "wind_gusts_10m"],
        #"forecast_days": 16,#i think it will be best to query results based off the date instead of searching up the dates just because of how the api doesn't always get the right range(actually giving the full dataframe could also be useful for multi questions)
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date,
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_uv_index = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()
    hourly_wind_gusts_10m = hourly.Variables(5).ValuesAsNumpy()

    meteo_time_zone = response.Timezone()
    meteo_time_zone = meteo_time_zone.decode()
    #print(meteo_time_zone)
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True).tz_convert(meteo_time_zone),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True).tz_convert(meteo_time_zone),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["uv_index"] = hourly_uv_index
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    #print("\nHourly data\n", hourly_dataframe)

    result = hourly_dataframe
    return result

def deduce_weather_result(prompt, weather_data):
    current_date = datetime.now().date()

    agent_prompt = f"""
    Break down the following prompt and deduce what kind of weather matches with the prompt.

    Prompt: {prompt}
    Current Date: {current_date}
    Weather Data: {weather_data}

    Based on the prompt you have been asked as well as the weather details provided answer the question the best you can.
    Remember not all details are needed unless specifically asked for.
    If no details are provided then just state the temperature and rain chance for 12pm
    Do not add any unesisary text make sure to get strait to the point.
    Here is a guide to an example formated output:
    Example:
    The weather in hawthorne at 12pm will be:
    Tempreture: 16.1 degrees
    Chance of rain: 65%
    Precipitation amount: 2.5 mm
    Wind Speed: 2km/h
    Max wind gust: 5km/h
    UV index: 1.27

    """

    extracted_details = weather_agent.generate_reply(messages=[{"role": "user", "content": agent_prompt}])
    print("#####################################")
    print("Resulting weather based off request")
    print("#####################################")
    print(extracted_details["content"])

    result = extracted_details["content"]
    return result

weather = obtain_weather_details("What is the weather in Pakenham victoria tomorrow at 3pm?")
#weather = obtain_weather_details("What is the weather in Sydney tomorrow?")
print("\n\n\n\n\n\n########## Weather reading ##########")
print(weather)
