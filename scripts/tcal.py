from datetime import datetime

from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from dotenv import load_dotenv
from icalendar import (
    Calendar as Calendar2,  # different to ics Calendar. if we get to cleaning up the code i could look into finding a way to just use one. for now to make things quicker i will keep both
)
from ics import Calendar, Event
from openai import OpenAI
from pydantic import BaseModel
from pytz import timezone
from tzlocal import get_localzone

# https://medium.com/@ethanbrooks42/build-your-first-llm-powered-productivity-app-with-openai-step-by-step-guide-to-automate-your-1a0eea6d7443
# https://www.geeksforgeeks.org/python/python-pytz/
# https://github.com/sensidev/ics2text/blob/main/ics2text.py#L92

llm_config = {
    "api_type": "ollama",
    "model": "gemma3",
}


user_proxy = UserProxyAgent(
    name="User_proxy",
    human_input_mode="ALWAYS",
    code_execution_config=False,
    description="A human user capable of working with Autonomous AI Agents.",
)

# I reckon this could be the better name for the agent as then it can be used for more broad tasks than just the callender
file_handler_agent = ConversableAgent(
    name="file_handler",
    system_message="""Your Job is to assist the user with their tasks.
    """,
    llm_config=llm_config,
    human_input_mode="NEVER",  # Never ask for human input.
)


# takes in a ics file and puts the content into more readable text making it easier for the LLM to read
def convert_ics_to_text(ics_file_path):
    local_time_zone = get_localzone()
    local_time_zone = str(local_time_zone)
    matching_events = []

    with open(ics_file_path, "r", encoding="utf-8") as file:
        # Load the calendar
        calendar = Calendar2.from_ical(file.read())

        # Iterate through calendar components
        for component in calendar.walk():
            # matching_events = []#moved to hear to prevent duplicats
            if component.name == "VEVENT":
                summary = str(component.get("SUMMARY"))
                description = str(component.get("DESCRIPTION"))
                attendees = component.get("ATTENDEE")
                attendees_list = []

                # Ensure attendees are in a list format
                if attendees:
                    if not isinstance(attendees, list):
                        attendees = [attendees]
                    attendees_list = [attendee.to_ical().decode("utf-8").split(":")[1] for attendee in attendees]
                start_time = component.get("DTSTART").dt
                start_time = start_time.astimezone(timezone(local_time_zone))
                start_time = start_time.strftime("%Y-%m-%d %H:%M")

                try:
                    end_time = component.get("DTEND").dt
                    try:
                        end_time = end_time.astimezone(timezone(local_time_zone))
                        end_time = end_time.strftime("%Y-%m-%d %H:%M")
                    except:
                        end_time = start_time
                except:
                    end_time = component.get("DTEND")
                    try:
                        end_time = end_time.astimezone(timezone(local_time_zone))
                        end_time = end_time.strftime("%Y-%m-%d %H:%M")
                    except:
                        end_time = start_time

                event_info = {
                    "Event": summary,
                    "Description": description,
                    "Start": start_time,
                    "End": end_time,
                }
                matching_events.append(event_info)
    return matching_events


# Takes in a users request or potentialy a formated request by another LLM agent and then the file_handeler agent converts it into what it belives would be the best names, descriptions times etc.
def format_user_request(tasks: str, current_date):
    prompt = f"""
    Break down the following tasks into realistic time frames, using the provided start time as a reference.

    Tasks: {tasks}
    Current Date: {current_date}

    Respond with a schedule in a structured format suitable for creating a calendar file (e.g., Task Name, Description, Start Time, End Time).
    Use 24 hour notation for times to make it unambiguous.
    Only give a date if specified by either the Tasks or Preferences otherwise use the current date instead
    Directly and only answer with the follow format:
    1. Task: Research for Report
    Date: 2022-07-13
    Description: Research reliable details online
    Start: 09:00
    End: 09:30

    2. Task: Write Draft
    Date: 2022-07-13
    Description: Handwriten reaserch report about computers
    Start: 09:30
    End: 10:00
    ...
    """

    result = file_handler_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    return result


# based on the file handeler agents formated response it converts it into an ics file which a user can upload to their calender.
def create_ics_file(schedule_text, file_name):
    # Initialize the calendar
    calendar = Calendar()

    # Parsing the LLM response
    task_date = ""
    for line in schedule_text.splitlines():
        if "Task:" in line:
            task_name = line.split(": ")[1].strip()
        elif "Description:" in line:
            task_description = line.split(": ")[1].strip()
        elif "Date:" in line:
            task_date = line.split(": ")[1].strip()
        elif "Start:" in line:
            if task_date == "":  # more extensive error checking will be needed for wrong formats for both date and time
                print("Error collecting the date")
            else:
                local_time_zone = get_localzone()
                local_time_zone = str(local_time_zone)
                start_time_str = line.split(": ")[1].strip()
                # Parse the start time, adding today's date
                start_time = datetime.strptime(f"{task_date} {start_time_str}", "%Y-%m-%d %H:%M")
                start_time = timezone(local_time_zone).localize(start_time)
        elif "End:" in line:
            if task_date == "":  # more extensive error checking will be needed for wrong formats for both date and time
                print("Error collecting the date")
            else:
                local_time_zone = get_localzone()
                local_time_zone = str(local_time_zone)
                end_time_str = line.split(": ")[1].strip()
                # Parse the end time, adding today's date
                end_time = datetime.strptime(f"{task_date} {end_time_str}", "%Y-%m-%d %H:%M")
                end_time = timezone(local_time_zone).localize(end_time)

                # Create a calendar event
                event = Event()
                event.name = task_name
                if task_description:
                    event.description = task_description
                event.begin = start_time
                event.end = end_time
                calendar.events.add(event)

    # Write to .ics file
    with open(file_name, "w") as f:
        f.writelines(calendar)
    print("ics file created")

    return file_name


# This function first converts a specified ics file to text from which the LLM agent formats its content into readable text
def agent_read_calender(file_name):
    calender_content = convert_ics_to_text(file_name)

    prompt = f"""
    You are to explain what the date, tasks and times are based off this ics calender.

    calender content: {calender_content}

    Respond with a list of each task and their related time for the date provided. also convert the time to 24 hour format such as 16:15 pm.
    Make sure to convert these times from UCD to the provided timezone.
    Follow the example format bellow and do not add anything else.
    EXAMPLE:
    1. Task: Research for Report
    Date: 2022-07-13
    Description: Research reliable details online
    Start: 09:00
    End: 09:30

    2. Task: Write Draft
    Date: 2022-07-13
    Description: Handwriten reaserch report about computers
    Start: 09:30
    End: 10:00
    """

    result = file_handler_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    return result


# this function takes in a user/agent task creation request as well as a ics file to consider when making a new scedual and a new one to write an updated scedual to.
def agent_read_and_write_calender(tasks: str, current_date, file_name_read, file_name_write):
    calender_dates = convert_ics_to_text(file_name_read)

    # uses the extracted calender dates to create a new scedual.
    extracted_prompt = f"""
    Break down the following tasks into realistic time frames, using the provided start time as a reference.

    Tasks: {tasks}
    Current Date: {current_date}
    Pre Existing Plans: {calender_dates}

    Respond with a schedule in a structured format suitable for creating a calendar file (e.g., Task Name, Description, Start Time, End Time).
    Use 24 hour notation for times to make it unambiguous.
    Only give a date if specified by either the Tasks or Preferences otherwise use the current date instead
    Do not clash any new sceduals with pre existing plans.
    Make sure to add all pre existing plans to this new scedual.
    Directly and only answer with the follow format:
    1. Task: Research for Report
    Date: 2022-07-13
    Description: Research reliable details online
    Start: 09:00
    End: 09:30

    2. Task: Write Draft
    Date: 2022-07-13
    Description: Handwriten reaserch report about computers
    Start: 09:30
    End: 10:00
    ...
    """
    result = file_handler_agent.generate_reply(messages=[{"role": "user", "content": extracted_prompt}])
    print("#####################################")
    print("New callender dates content")
    print("#####################################")
    print(result["content"])

    # creates new scedual here
    create_ics_file(result["content"], file_name_write)

    return result


# change the task number to try out each scenario (TEMPORARY)
task = 7
if task == 1:
    print("task 1")
    ics_file = file_name = "Daily_Schedule.ics"
    result = format_user_request(
        "Maths at 10am for two hours, english at 6pm for 1 hour and history at 12pm tommorow", datetime.now().date()
    )
    print(result["content"])
    print("\n")
    create_ics_file(result["content"], ics_file)
elif task == 2:
    print("task 2")
    ics_file = file_name = "Daily_Schedule.ics"
    result = agent_read_calender(ics_file)
    print(result["content"])
elif task == 3:
    print("task 3")
    file_name_read = "Daily_Schedule.ics"  # which it will read the users ics schedule from
    file_name_write = "Daily_Schedule_reformated.ics"  # the new file it will create a new schedule for
    result = agent_read_and_write_calender(
        "Between maths and english book me a 1 hour meeting with Anton.",
        datetime.now().date(),
        file_name_read,
        file_name_write,
    )
elif task == 4:
    print("task 4")
    ics_file = file_name = "export.ics"  # testing if it can read a export from the read calender app
    result = agent_read_calender(ics_file)
    print(result["content"])
elif task == 5:
    print("task 5")
    ics_file = file_name = "Demo1.ics"
    print("\n")
    tasks = input("Enter the tasks you would like to schedule here -->")
    print("\n")

    result = format_user_request(tasks, datetime.now().date())
    print(result["content"])
    print("\n")
    create_ics_file(result["content"], ics_file)
elif task == 6:
    print("task 6")
    ics_file = file_name = "Demo1.ics"
    result = agent_read_calender(ics_file)
    print(result["content"])
elif task == 7:
    print("task 7")
    print("\n")
    print("\n")
    tasks = input("Enter the tasks you would like to schedule here -->")
    print("\n")
    file_name_read = "Demo1.ics"  # which it will read the users ics schedule from
    file_name_write = "Demo2.ics"  # the new file it will create a new schedule for
    result = agent_read_and_write_calender(tasks, datetime.now().date(), file_name_read, file_name_write)
else:
    print("no task selected")

# To do still:
# - Test with a stronger LLM
# - Add comprehensive error checking
# - Clean up code and naming conventions (partialy done)
# - Intergrate code with main MAS
