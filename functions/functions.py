from calendar import calendar
from datetime import timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dateutil import parser
from functions.google_api import create_service


def format_class_details(data, class_id):
    string = ""
    string = string + \
        f"*ℹ️ Class Details*\n*Type:* {data['class_type']}\n*Number of Students:* {data['num_of_students']}\n*Student Names:* {' , '.join(data['students'])}\n*Start Date(Tentative):* {data['start_date']}\n*Week Day:* {data['week_day']}\n*Time:* {data['class_time']}\n*Number Of Classes:* {data['num_classes']}\n*Course:* {data['course_name']}\n*Tutor:* {data['tutor']}\n*Parent's Email:* {data['parent_email']}\n*Parent's Number:* {data['parent_number']}\n*Status:* {data['status']}\n*Class ID:* `{class_id}`"

    return string


def format_class_confirmation(data):
    string = ""
    string = string + \
        f"*Type:* {data['class_type']}\n*Number of Students:* {data['num_of_students']}\n*Student Names:* {' , '.join(data['students'])}\n*Start Date(Tentative):* {data['start_date']}\n*Week Day:* {data['week_day']}\n*Time:* {data['class_time']}\n*Number Of Classes:* {data['num_classes']}\n*Course:* {data['course_name']}\n*Parent's Email:* {data['parent_email']}\n*Parent's Number:* {data['parent_number']}\n\n*What do you want to do?*"
    return string


def format_edit_class_confirmation(data, old):
    string = ""
    class_type = data['class_type']
    old_class_type = old['class_type']
    num_of_students = data['num_of_students']
    old_num_of_students = old['num_of_students']
    start_date = data['start_date']
    old_start_date = old['start_date']
    week_day = data['week_day']
    old_week_day = old['week_day']
    class_time = data['class_time']
    old_class_time = old['class_time']
    num_classes = data['num_classes']
    old_num_classes = old['num_classes']
    course_name = data['course_name']
    old_course_name = old['course_name']
    parent_email = data['parent_email']
    old_parent_email = old['parent_email']
    parent_number = data['parent_number']
    old_parent_number = old['parent_number']
    string = string + \
        f"*Type:* {old_class_type}*{' | ' + class_type if (class_type != old_class_type) else ''}*\n*Number of Students:* {old_num_of_students}*{' | ' + num_of_students if (num_of_students != old_num_of_students) else ''}*\n*Student Names:* {' , '.join(data['students'])}\n*Start Date(Tentative):* {old_start_date}*{' | ' + start_date if (start_date != old_start_date) else ''}*\n*Week Day:* {old_week_day}*{' | ' + week_day if (week_day != old_week_day) else ''}*\n*Time:* {old_class_time}*{' | ' + class_time if (class_time != old_class_time) else ''}*\n*Number Of Classes:* {old_num_classes}*{' | ' + num_classes if (num_classes != old_num_classes) else ''}*\n*Course:* {old_course_name}*{' | ' + course_name if (course_name != old_course_name) else ''}*\n*Parent's Email:* {old_parent_email}*{' | ' + parent_email if (parent_email != old_parent_email) else ''}*\n*Parent's Number:* {old_parent_number}*{' | ' + parent_number if (parent_number != old_parent_number) else ''}*\n\n*What do you want to do?*"
    return string


def format_surf(current, total, data):
    string = ""
    string = string + \
        f"*{current+1} of {total}*\n\n*ℹ️ Class Details*\n*Type:* {data['class_type']}\n*Number of Students:* {data['num_of_students']}\n*Student Names:* {' , '.join(data['students'])}\n*Start Date(Tentative):* {data['start_date']}\n*Week Day:* {data['week_day']}\n*Time:* {data['class_time']}\n*Number Of Classes:* {data['num_classes']}\n*Course:* {data['course_name']}\n"
    return string


def format_pending(name, data):
    string = ""
    string = string + \
        f"*👋 Hi There,*\n\n*{name}* wants to take a *{data['course_name']}* course on *{data['week_day']}* by {data['class_time']} WAT for a total of *{data['num_classes']}* classes, starting from {data['start_date']}"
    return string


def format_user_classes(header, data):
    string = ""
    string = string + \
        f"*{header}*\n*Type:* {data['class_type']}\n*Number of Students:* {data['num_of_students']}\n*Student Names:* {' , '.join(data['students'])}\n*Start Date:* {data['start_date']}\n*Week Day:* {data['week_day']}\n*Time:* {data['class_time']}\n*Number Of Classes:* {data['num_classes']}\n*Course:* {data['course_name']}\n*Status:* {data['status']}"
    return string


def format_edit_user_classes(header, data, old):
    string = ""
    class_type = data['class_type']
    old_class_type = old['class_type']
    num_of_students = data['num_of_students']
    old_num_of_students = old['num_of_students']
    start_date = data['start_date']
    old_start_date = old['start_date']
    week_day = data['week_day']
    old_week_day = old['week_day']
    class_time = data['class_time']
    old_class_time = old['class_time']
    num_classes = data['num_classes']
    old_num_classes = old['num_classes']
    course_name = data['course_name']
    old_course_name = old['course_name']
    string = string + \
        f"*{header}*\n*Type:* {old_class_type}*{' | ' + class_type if (class_type != old_class_type) else ''}*\n*Number of Students:* {old_num_of_students}*{' | ' + num_of_students if (num_of_students != old_num_of_students) else ''}*\n*Student Names:* {' , '.join(data['students'])}\n*Start Date(Tentative):* {old_start_date}*{' | ' + start_date if (start_date != old_start_date) else ''}*\n*Week Day:* {old_week_day}*{' | ' + week_day if (week_day != old_week_day) else ''}*\n*Time:* {old_class_time}*{' | ' + class_time if (class_time != old_class_time) else ''}*\n*Number Of Classes:* {old_num_classes}*{' | ' + num_classes if (num_classes != old_num_classes) else ''}*\n*Course:* {old_course_name}*{' | ' + course_name if (course_name != old_course_name) else ''}*\n*Status:* {data['status']}"
    return string


def format_tutor_details(data):
    string = ""
    string = string + \
        f"*ℹ️ Tutor Details*\n*Telegram ID:* {data['user_id']}\n*Name:* {data['name']}\n*Email:* {data['email']}\n*Active:* {data['active']}\n*Admin:* {data['admin']}\n*Pair Code:* `{data['_id']}`"

    return string


def decide_button(tutor, data):
    if tutor['admin']:
        if data['completed'] and data['report'] != "":
            return InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Show Report", callback_data=f"show_report_{data['_id']}"),
                        InlineKeyboardButton(
                            "Remove Report", callback_data=f"remove_report_{data['_id']}")
                    ],
                    [
                        InlineKeyboardButton(
                            "✔️ Done", callback_data="done"),
                    ]
                ]
            )

        elif data['completed'] and data['report'] == "":
            return InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Request Report", callback_data=f"request_report_{data['_id']}")
                    ]
                ]
            )
        elif data['tutor']:
            return InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "End Session", callback_data=f"end_session_{data['_id']}")
                    ]
                ]
            )
    else:
        if data['tutor']:
            return
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Take Class",
                        callback_data=f"take_{data['_id']}"
                    ),

                    InlineKeyboardButton(
                        "🚫 Not Avaliable",
                        callback_data=f"leave_{data['_id']}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"✔️ Done",
                        callback_data="done"
                    )
                ]
            ]
        )


def convert_date_time(date, time, buffer):
    date = parser.parse(date + " " + time, dayfirst=True)
    return (date + timedelta(hours=buffer)).replace(
        microsecond=0).isoformat()


def add_calander_event(data, tutor_email):

    CLIENT_SECRET_FILE = "creds.json"

    API_NAME = "calendar"

    API_VERSION = "v3"

    sendUpdates = "all"

    CALENDAR_ID = "9v52fr8c3n8n2dqogohnvgh9t8@group.calendar.google.com"

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    attendees = [{'email': f'{tutor_email}'}]

    for email in data['parent_email']:
        attendees.append({'email': f'{email}'})

    event = {
        'summary': 'Live Class',
        'description': f"{data['course_name']}",
        'start': {
            'dateTime': f"{convert_date_time(data['start_date'],data['class_time'],0)}",
            'timeZone': 'Africa/Lagos',
        },
        'end': {
            'dateTime': f"{convert_date_time(data['start_date'],data['class_time'],1)}",
            'timeZone': 'Africa/Lagos',
        },
        'recurrence': [
            f"RRULE:FREQ={'WEEKLY' if (data['week_day'] != 'Everyday') else 'DAILY'};COUNT={data['num_classes']}"
        ],
        'attendees': attendees,

        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }
    event_data = service.events().insert(
        calendarId=CALENDAR_ID,
        sendUpdates=sendUpdates,
        body=event
    ).execute()

    return event_data['id']


def delete_calendar_event(event_id):
    CLIENT_SECRET_FILE = "creds.json"

    API_NAME = "calendar"

    API_VERSION = "v3"

    CALENDAR_ID = "9v52fr8c3n8n2dqogohnvgh9t8@group.calendar.google.com"

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    service.events().delete(
        calendarId=CALENDAR_ID,
        eventId=event_id
    ).execute()
    return
