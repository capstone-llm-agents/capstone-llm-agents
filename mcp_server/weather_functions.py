from datetime import datetime, timedelta

import openmeteo_requests
import pandas as pd
import requests_cache
from autogen import ConversableAgent
from retry_requests import retry
import os
from dotenv import load_dotenv
import re

load_dotenv()
########llm agent setup########
Model_type = 2 #use 1 for gemma3 or 2 for openai

if Model_type == 1:
    llm_config = {
        "api_type": "ollama",
        "model": "gemma3",
    }
elif Model_type == 2:
    llm_config = {
        "api_type": "openai",
        "model": "gpt-4o-mini",
        "api_key": os.environ.get("OPENAI_API_KEY"),
    }
else:
    print("No model has been selected in weather_functions.py")

weather_agent = ConversableAgent(
    name="weather_agent",
    system_message="""Your Job is to assist the user with their tasks.
    """,
    llm_config=llm_config,
    human_input_mode="NEVER",
)
########llm agent setup########


def generate_weather_data(latitude, longitude, start_date, end_date, time, time_zone):

    # Setup the Open-Meteo API client with cache and retry on error
    print("###Time zone and time inputed###")
    print(time_zone)
    print(time)
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "uv_index",
            "precipitation_probability",
            "precipitation",
            "wind_speed_10m",
            "wind_gusts_10m",
        ],
        # "forecast_days": 16,#i think it will be best to query results based off the date instead of searching up the dates just because of how the api doesn't always get the right range(actually giving the full dataframe could also be useful for multi questions)
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date,
    }
    responses = openmeteo.weather_api(url, params=params)


    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]



    if time_zone == response.Timezone().decode('utf-8'):
        print("no changes needed")
        new_date = start_date
        new_time = time
    else:
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": [
                "temperature_2m",
                "uv_index",
                "precipitation_probability",
                "precipitation",
                "wind_speed_10m",
                "wind_gusts_10m",
            ],
            # "forecast_days": 16,#i think it will be best to query results based off the date instead of searching up the dates just because of how the api doesn't always get the right range(actually giving the full dataframe could also be useful for multi questions)
            "timezone": time_zone,
            "start_date": start_date,
            "end_date": end_date,
        }
        second_responses = openmeteo.weather_api(url, params=params)

        second_responses = second_responses[0]

        print("Auto timezone responses")
        print("new time in seconds is")
        print(response.UtcOffsetSeconds())
        print("the new time in minutes is")
        minutes = (response.UtcOffsetSeconds() / 60)
        print(minutes)
        print("the new time in hours is")
        hours = (minutes / 60)
        print(hours)

        print("chosen timezone responses")
        print("new time in seconds is")
        print(second_responses.UtcOffsetSeconds())
        print("the new time in minutes is")
        second_minutes = (second_responses.UtcOffsetSeconds() / 60)
        print(second_minutes)
        print("the new time in hours is")
        second_hours = (second_minutes / 60)
        print(second_hours)

        print("final time adjustment in hours")
        time_difference = (second_hours - hours)#needs to be this way so the target is subtracted from the locations timezone
        print(time_difference)

        if time_difference < 0:
            is_negative = True
        else:
            is_negative = False
        new_date = None
        new_time = None
        change_date = 0#if this changes to 1 then date needs to go a day forward. If -1 then back a day. if 0 keep current date

        adjusted_time = time.split(":")[0].strip()
        adjusted_time = int(adjusted_time)
        print("###Original time###")
        print(adjusted_time)
        i = 0
        while i < abs(time_difference):#has to temp make positive
            if is_negative == True:
                if adjusted_time != 0:
                    adjusted_time = (adjusted_time - 1)
                else:
                    adjusted_time = 23
                    change_date = - 1
            else:
                if adjusted_time != 23:
                    adjusted_time = (adjusted_time + 1)
                else:
                    adjusted_time = 0
                    change_date = + 1
            i = (i + 1)
        if len(str(adjusted_time)) == 1:
            adjusted_time = "0" + str(adjusted_time) + ":00"
        else:
            adjusted_time = str(adjusted_time) + ":00"
        new_time = adjusted_time
        print("###the new time is###")
        print(new_time)
        if change_date == 0:
            print("The date doesn't need to be changed")
            new_date = start_date
        elif change_date == 1:
            print("the date needs to be moved one date forward")
            print("initial date -> " + start_date)
            date_1 = datetime.strptime(start_date, "%Y-%m-%d")
            new_date = date_1 + timedelta(days=1)
            new_date = new_date.strftime("%Y-%m-%d")
            print("new date -> " + new_date)
        else:
            print("the date needs to be moved one day back")
            print("initial date -> " + start_date)
            date_1 = datetime.strptime(start_date, "%Y-%m-%d")
            new_date = date_1 + timedelta(days=-1)
            new_date = new_date.strftime("%Y-%m-%d")
            print("new date -> " + new_date)



    #this will create the results needed for the actual date
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "uv_index",
            "precipitation_probability",
            "precipitation",
            "wind_speed_10m",
            "wind_gusts_10m",
        ],
        # "forecast_days": 16,#i think it will be best to query results based off the date instead of searching up the dates just because of how the api doesn't always get the right range(actually giving the full dataframe could also be useful for multi questions)
        "timezone": "auto",
        "start_date": new_date,
        "end_date": new_date,
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
    # print(meteo_time_zone)
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert(meteo_time_zone),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert(meteo_time_zone),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["uv_index"] = hourly_uv_index
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    # print("\nHourly data\n", hourly_dataframe)

    result = hourly_dataframe
    return [result, new_date, adjusted_time]


def deduce_weather_result(time_zone, time, weather_data):
    #current_date = datetime.now().date()

    agent_prompt = f"""
    Break down the following prompt and deduce what kind of weather matches with the Location and Time.

    Time zone: {time_zone}
    Time used: {time}
    Weather Data: {weather_data}

    Based on the weather details provided Reformat the data to the provided example.
    Remember to keep your responses small and concise.
    Do not add any unesisary text.
    Always use the timezone provided in your answer.
    Only ever use the time from (Time used:)
    Be careful when reading the time as you will likely see an output such as xx:xx:00+xx:00. do not add the additional time only use the first part within the weather data i.e. the "xx:xx" part
    Here is a guide to an example formatted output:
    Example:
    Using Australia/Melbourne as the timezone reference point, The weather in Rosedale at 4pm 12/07/2025 will be:
    Temperature: 14.1 degrees
    Chance of rain: 35%
    Precipitation amount: 1.0 mm
    Wind Speed: 3km/h
    Max wind gust: 7km/h
    UV index: 0.32

    """

    extracted_details = weather_agent.generate_reply(messages=[{"role": "user", "content": agent_prompt}])
    print("#####################################")
    print("Resulting weather based off request")
    print("#####################################")
    if Model_type == 1:#used to acount for different LLM ways of extracting data
        LLM_details = extracted_details["content"]
        print(LLM_details)
    elif Model_type == 2:
        LLM_details = extracted_details
        print(LLM_details)
    else:
        print("Error within weather_server.py response collection")

    result = LLM_details
    return result


def break_down_result(weather_data, time, location):
    for index, row in weather_data.iterrows():
        # print("###########new_row###############")
        # print(str(row["date"]))
        if time in str(row["date"]):
            data_found = str(row)
            # print(data_found)

    data_found = data_found + "\n Reading location: " + location
    return data_found
