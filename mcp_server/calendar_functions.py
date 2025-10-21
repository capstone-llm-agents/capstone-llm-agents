"""Calendar functions for the calendar server."""

from datetime import datetime

from icalendar import Calendar as Calendar2
from ics import Calendar, Event
from pytz import timezone
from tzlocal import get_localzone


# takes in a ics file and puts the content into more readable text making it easier for the LLM to read
def convert_ics_to_text(ics_file_path):
    #print(This_will_not_work)#used to test the error catching
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


# based on the file handeler agents formated response it converts it into an ics file which a user can upload to their calender.
def create_ics_file(schedule_text, file_name):
    # Initialize the calendar
    #print(This_will_not_work)#used to test the error catching
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
