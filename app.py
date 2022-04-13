import os
from bson.objectid import ObjectId
import re
import logging
import calendar
from dateutil import parser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from db.db import accept_editted_class, add_user_to_reject_list, approve, decline, decline_editted_class, delete_report, end_class_session, get_admins, get_all_classes, get_tutor, create_new_tutor, check_pair_id, get_user_classes, pair_tutor, create_class, get_all_tutors, get_pending_classes, csv_classes, get_class, csv_tutors, get_tutorless_classes, assign_to_class, search_classes, search_tutors, store_calendar_event_id, submit_new_class_details, submit_report, toggle_active, toggle_admin
from functions.functions import add_calander_event, decide_button, delete_calendar_event, format_class_details, format_edit_class_confirmation, format_edit_user_classes, format_surf, format_class_confirmation, format_pending, format_tutor_details, format_user_classes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Convo States
COLLECTING_NAME, COLLECTING_EMAIL, COLLECTING_CODE, COLLECTING_CLASS_TYPE, COLLECTING_COURSE_NAME, COLLECTING_NUMBER_OF_CLASSES, COLLECTING_NUMBER_OF_STUNDETS, COLLECTING_STUDENT_NAME, COLLECTING_START_DATE, COLLECTING_TIME, COLLECTING_PARENTS_NUMBER, COLLECTING_PARENTS_EMAIL, COLLECTING_WHAT, COLLECTING_BY, COLLECTING_QUERY, COLLECTING_REPORT = range(
    16)

# Variable to end convo
END = ConversationHandler.END


# Keyboard
cancel_keybaord = ReplyKeyboardMarkup([
    [
        KeyboardButton("🚫 Cancel")
    ]
],
    resize_keyboard=True,
)

home_layout_normal = ReplyKeyboardMarkup([
    [KeyboardButton("Surf Classes"), KeyboardButton("My Classes")],
    [KeyboardButton('Help')]

],
    resize_keyboard=True
)

home_layout_admin = ReplyKeyboardMarkup([
    [
        KeyboardButton("Pending"),
        KeyboardButton("Classes"),
        KeyboardButton("Tutors")
    ],
    [KeyboardButton("Help")]

],
    resize_keyboard=True
)

class_menu_layout = ReplyKeyboardMarkup([
    [
        KeyboardButton("Add Class"),
        KeyboardButton("Export Classes"),
    ],
    [KeyboardButton("🏠 Main Menu")]

],
    resize_keyboard=True
)

tutor_menu_layout = ReplyKeyboardMarkup([
    [
        KeyboardButton("Add Tutor"),
        KeyboardButton("Export Tutors"),
    ],
    [KeyboardButton("🏠 Main Menu")]

],
    resize_keyboard=True
)


# funtions
def clear_user_data(context: CallbackContext):
    user_data = context.user_data
    user_data['last_message_id'] = ""
    user_data['old_class_details'] = ""
    user_data['class_type'] = ""
    user_data['num_of_students'] = ""
    user_data['students'] = ""
    user_data['start_date'] = ""
    user_data['class_time'] = ""
    user_data['num_classes'] = ""
    user_data['course_name'] = ""
    user_data['parent_email'] = ""
    user_data['parent_number'] = ""


def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    clear_user_data(context)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return

    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return
    context.bot.send_message(
        chat_id=user_id,
        text=f"👋 *Hi {tutor['name']}*, How can i be of help?",
        parse_mode="Markdown",
        reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal
    )


def echo(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=user_id,
        text="I don't quite understand what you mean",
        parse_mode="Markdown"
    )


# Help Function
def help(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    if tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            # TODO add help info for admins
            text="Help info for admin",
            parse_mode="Markdown"
        )
        return END
    context.bot.send_message(
        chat_id=user_id,
        # TODO add help info for tutors
        text="Help info for tutors",
        parse_mode="Markdown"
    )
    return END


# Cancel Function
def cancel(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    clear_user_data(context)
    context.bot.send_message(
        chat_id=user_id,
        text="🚫 Canceled",
        parse_mode="Markdown",
        reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal
    )
    return END


def main_menu(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    context.bot.send_message(
        chat_id=user_id,
        text="Main Menu",
        parse_mode="Markdown",
        reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal
    )
    return END


# Functions to create Tutor
def create_tutor(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return END
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return END

    if not tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            text="Sorry only *admins* can do that.",
            parse_mode="Markdown",
        )
        return END

    context.bot.send_message(
        chat_id=user_id,
        text="Enter a *NAME* for this tutor: ",
        parse_mode="Markdown",
        reply_markup=cancel_keybaord
    )
    return COLLECTING_NAME


def store_name(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['Name'] = text
    context.bot.send_message(
        chat_id=user_id,
        text="Enter an *EMAIL* for this tutor: ",
        parse_mode="Markdown"
    )
    return COLLECTING_EMAIL


def invalid_name(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=user_id,
        text="*Invalid* name. First and Last Name should be separated by space. Enter *NAME* for this tutor: ",
        parse_mode="Markdown"
    )
    return COLLECTING_NAME


def store_email(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['Email'] = text
    tutor = get_tutor(user_id)
    code = create_new_tutor(
        user_data['Name'],
        user_data['Email'],
        get_tutor(user_id)['name']
    )
    context.bot.send_message(
        chat_id=user_id,
        text=f"Account Created. Here's the pairing code for *{user_data['Name']}* `{code}`",
        parse_mode="Markdown",
        reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal
    )
    return END


def invalid_email(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=user_id,
        text="*Invalid* email please enter a valid *EMAIL* for this tutor: ",
        parse_mode="Markdown"
    )
    return COLLECTING_EMAIL
# End of funtions to create Tutors


# Functions to coonect Tutor Account
def connect_account(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    if tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="You Seem to already be connected to an account.",
            parse_mode="Markdown",
        )
        return END
    context.bot.send_message(
        chat_id=user_id,
        text="Enter *PAIRING* code: ",
        parse_mode="Markdown",
        reply_markup=cancel_keybaord
    )
    return COLLECTING_CODE


def link_code(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    pair_id = update.message.text
    if not check_pair_id(pair_id):
        context.bot.send_message(
            chat_id=user_id,
            text="*Invalid* that code doesn't look right. Enter *PAIRING* code: ",
            parse_mode="Markdown"
        )
        return COLLECTING_CODE

    if not pair_tutor(user_id, pair_id):
        context.bot.send_message(
            chat_id=user_id,
            text="An Error occured. Please try again later",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return END
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="An Error occured. Please try again later",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return END
    context.bot.send_message(
        chat_id=user_id,
        text=f"Connected Successfully. Welcome {tutor['name']}",
        parse_mode="Markdown",
        reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal
    )
    return END


def invalid_code(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=user_id,
        text="*Invalid* that code doesn't look right. Enter *PAIRING* code: ",
        parse_mode="Markdown"
    )
    return COLLECTING_CODE
# End Functions to connect Tutor Account


# Function to show pendiing requests
def show_pending(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return END
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return END
    if not tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            text="Sorry only *admins* can do that.",
            parse_mode="Markdown"
        )
        return END
    chunk = get_pending_classes()
    if not chunk:
        context.bot.send_message(
            chat_id=user_id,
            text="😮‍💨 No Pending Request",
            parse_mode="Markdown"
        )
        return
    for data in chunk:
        text = format_pending(get_tutor(data['tutor'])['name'], data)
        context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✅ Approve",
                            callback_data=f"approve_{data['tutor']}_{data['_id']}"
                        ),

                        InlineKeyboardButton(
                            "🚫 Decline",
                            callback_data=f"decline_{data['tutor']}_{data['_id']}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🕰️ Change Class Details",
                            callback_data=f"change_details_{data['_id']}"
                        )
                    ]
                ]
            )
        )

    return END


# Function to show all classes
def class_menu(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return END
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return END
    if not tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            text="Sorry only *admins* can do that.",
            parse_mode="Markdown"
        )
        return END
    context.bot.send_message(
        chat_id=user_id,
        text="Class Menu",
        reply_markup=class_menu_layout
    )
    return END


def show_classes(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return END
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return END
    if not tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            text="Sorry only *admins* can do that.",
            parse_mode="Markdown"
        )
        return END
    filepath = csv_classes()
    context.bot.send_document(
        chat_id=user_id,
        document=open(filepath, 'rb'),
        caption="*Here is a csv file containing all classes*",
        parse_mode="Markdown"
    )
    return END


# Function to show all tutors
def tutor_menu(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return END
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return END
    if not tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            text="Sorry only *admins* can do that.",
            parse_mode="Markdown"
        )
        return END
    context.bot.send_message(
        chat_id=user_id,
        text="Tutor Menu",
        reply_markup=tutor_menu_layout
    )
    return END


def show_tutors(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return END
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return END
    if not tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            text="Sorry only *admins* can do that.",
            parse_mode="Markdown"
        )
        return END
    filepath = csv_tutors()
    context.bot.send_document(
        chat_id=user_id,
        document=open(filepath, 'rb'),
        caption="*Here is a csv file containing all tutors*",
        parse_mode="Markdown"
    )
    return END


# Functions to add class
def add_class(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return END
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return END
    if not tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            text="Sorry only *admins* can do that.",
            parse_mode="Markdown",
        )
        return END
    user_data['last_message_id'] = []
    user_data['last_message_id'].append(context.bot.send_message(
        chat_id=user_id,
        text="Enter Class Type(PT,VG or with -E): ",
        parse_mode="Markdown",
        reply_markup=cancel_keybaord
    ).message_id
    )
    return COLLECTING_CLASS_TYPE


def invalid_type(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['class_type']}`"
    except:
        pass
    user_data['last_message_id'].append(context.bot.send_message(
        chat_id=user_id,
        text=f"*Invalid Input*. Enter Class Type(PT,VG or with -E (PT-E & VG-E) for everyday classes) {string if (string != '') else ''}: ",
        parse_mode="Markdown"
    ).message_id
    )
    return COLLECTING_CLASS_TYPE


def store_type(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['class_type'] = text
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['num_of_students']}`"
    except:
        pass
    user_data['last_message_id'].append(context.bot.send_message(
        chat_id=user_id,
        text=f"Enter Number Of Students {string if (string != '') else ''}: ",
        parse_mode="Markdown"
    ).message_id
    )
    return COLLECTING_NUMBER_OF_STUNDETS


def store_number_of_students(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['num_of_students'] = text
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{','.join(old_data['students'])}`"
    except:
        pass
    user_data['last_message_id'].append(context.bot.send_message(
        chat_id=user_id,
        text=f"Enter Names Of Students(separete by comma) {string if (string != '') else ''}: ",
        parse_mode="Markdown"
    ).message_id
    )
    return COLLECTING_STUDENT_NAME


def invalid_number(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['num_of_students']}`"
    except:
        pass
    user_data['last_message_id'].append(context.bot.send_message(
        chat_id=user_id,
        text=f"*Invalid Input*. Enter Number Of Students {string if (string != '') else ''}: ",
        parse_mode="Markdown"
    ).message_id
    )
    return COLLECTING_NUMBER_OF_STUNDETS


def store_student_names(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    names = text.split(",")
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    if len(names) != int(user_data['num_of_students']):
        try:
            old_data = user_data['old_class_details']
            string = f"or `{','.join(old_data['students'])}`"
        except:
            pass
        user_data['last_message_id'].append(
            context.bot.send_message(
                chat_id=user_id,
                text=f"Number of students doesn't match provided. Enter {user_data['num_of_students']} Names of Students(separete by comma) {string if (string != '') else ''}: ",
                parse_mode="Markdown"
            ).message_id
        )
        return COLLECTING_STUDENT_NAME
    user_data['students'] = names
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['start_date']}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"Enter Tentative Start Date For Class(dd-mm-yyyy) {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_START_DATE


def store_start_date(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['start_date'] = text
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['class_time']}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"Enter A Time For This Class(24hrs format) {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_TIME


def invalid_start_date(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['start_date']}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"*Invalid Input*. Enter Tentative Start Date For Class(e.g 20-09-2021) {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_START_DATE


def store_class_time(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['class_time'] = text
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['num_classes']}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"Enter Number Of Classes {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_NUMBER_OF_CLASSES


def invalid_class_time(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['class_time']}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"*Invalid Input*. Enter A Time For This Class(e.g 09:00 or 13:20) {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_TIME


def store_num_classes(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['num_classes'] = text
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['course_name']}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"Enter Course Name {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_COURSE_NAME


def invalid_num_classes(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['num_classes']}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"*Invalid Input*. Enter Number Of Classes {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_NUMBER_OF_CLASSES


def store_course_name(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['course_name'] = text
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{','.join(old_data['parent_email'])}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"Enter Parent's Email {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_PARENTS_EMAIL


def store_parent_email(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    emails = text.split(",")
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    if len(emails) != int(user_data['num_of_students']):
        try:
            old_data = user_data['old_class_details']
            string = f"or `{','.join(old_data['parent_email'])}`"
        except:
            pass
        user_data['last_message_id'].append(
            context.bot.send_message(
                chat_id=user_id,
                text=f"*Invalid Input*. Enter Parent's Email For Every Student {string if (string != '') else ''}: ",
                parse_mode="Markdown"
            ).message_id
        )
        return COLLECTING_PARENTS_EMAIL
    for email in emails:
        if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            try:
                old_data = user_data['old_class_details']
                string = f"or `{','.join(old_data['parent_email'])}`"
            except:
                pass
            user_data['last_message_id'].append(
                context.bot.send_message(
                    chat_id=user_id,
                    text=f"*Invalid Input*. Enter A Vaild Email For Every Student (test@email.com) {string if (string != '') else ''}: ",
                    parse_mode="Markdown"
                ).message_id
            )
            return COLLECTING_PARENTS_EMAIL
    user_data['parent_email'] = emails
    try:
        old_data = user_data['old_class_details']
        string = f"or `{','.join(old_data['parent_number'])}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"Enter Parent's Phone Number For Every Student {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_PARENTS_NUMBER


def store_parent_number(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    numbers = text.split(",")
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    if len(numbers) != int(user_data['num_of_students']):
        try:
            old_data = user_data['old_class_details']
            string = f"or `{','.join(old_data['parent_number'])}`"
        except:
            pass
        user_data['last_message_id'].append(
            context.bot.send_message(
                chat_id=user_id,
                text=f"*Invalid Input*. Enter Parent's Number For Every Student {string if (string != '') else ''}: ",
                parse_mode="Markdown"
            ).message_id
        )
        return COLLECTING_PARENTS_NUMBER
    for number in numbers:
        if not re.match(r'^\+(?:[0-9]●?){6,14}[0-9]$', number):
            try:
                old_data = user_data['old_class_details']
                string = f"or `{','.join(old_data['parent_number'])}`"
            except:
                pass
            user_data['last_message_id'].append(
                context.bot.send_message(
                    chat_id=user_id,
                    text=f"*Invalid Input*. Enter Valid Number For Every Student (e.g +234123456789) {string if (string != '') else ''}: ",
                    parse_mode="Markdown"
                ).message_id
            )
            return COLLECTING_PARENTS_NUMBER
    user_data['parent_number'] = numbers
    # Delete all message
    for message_id in user_data['last_message_id']:
        context.bot.delete_message(
            chat_id=user_id,
            message_id=message_id
        )
    user_data['last_message_id'] = []
    data = {
        "class_type": user_data['class_type'],
        "num_of_students": user_data['num_of_students'],
        "students": user_data['students'],
        "start_date": user_data['start_date'],
        "week_day": calendar.day_name[parser.parse(user_data['start_date'], dayfirst=True).weekday()] if ("E" not in str(user_data['class_type'])) else "Everyday",
        "class_time": user_data['class_time'],
        "num_classes": user_data['num_classes'],
        "course_name": user_data['course_name'],
        "parent_email": user_data['parent_email'],
        "parent_number": user_data['parent_number']
    }
    try:
        user_data['old_class_details']['class_type']
        context.bot.send_message(
            chat_id=user_id,
            text=format_edit_class_confirmation(
                data, user_data['old_class_details']),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✅ Do it",
                            callback_data="submit_edit"
                        ),
                        InlineKeyboardButton(
                            "🚫 Cancel",
                            callback_data="cancel_class_creation"
                        )
                    ]
                ]
            )
        )
        return END
    except:
        context.bot.send_message(
            chat_id=user_id,
            text=format_class_confirmation(data),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "👩‍🏫 Create Class",
                            callback_data="create_class"
                        ),

                        InlineKeyboardButton(
                            "📢 Create & Broadcast",
                            callback_data="create_broadcast"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🚫 Cancel",
                            callback_data="cancel_class_creation"
                        )
                    ]
                ]
            )
        )
        return END


def invalid_parent_number(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    user_data['last_message_id'].append(update.effective_message.message_id)
    string = ''
    try:
        old_data = user_data['old_class_details']
        string = f"or `{old_data['parent_number']}`"
    except:
        pass
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"*Invalid Input*. Enter Parent's Number(e.g +234123456789) {string if (string != '') else ''}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_PARENTS_NUMBER


def create_new_class(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    query = update.callback_query
    tutor = get_tutor(user_id)
    user_data = context.user_data
    try:
        data = {
            "class_type": user_data['class_type'],
            "num_of_students": user_data['num_of_students'],
            "students": user_data['students'],
            "start_date": user_data['start_date'],
            "week_day": calendar.day_name[parser.parse(user_data['start_date'], dayfirst=True).weekday()] if ("E" not in str(user_data['class_type'])) else "Everyday",
            "class_time": user_data['class_time'],
            "num_classes": user_data['num_classes'],
            "course_name": user_data['course_name'],
            "parent_email": user_data['parent_email'],
            "parent_number": user_data['parent_number']
        }
        query.answer()
        class_id = create_class(data, tutor['name'])
        data = get_class(class_id)
        query.edit_message_text(
            text=format_class_details(data, class_id),
            parse_mode="Markdown"
        )
        context.bot.send_message(chat_id=user_id, text="Main Menu", reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal)
        clear_user_data()
        return
    except KeyError:
        query.edit_message_text(
            text="*Token Expired. Please Try Again*",
            parse_mode="Markdown"
        )
        context.bot.send_message(chat_id=user_id, text="Main Menu", reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal)
        clear_user_data()
        return


def create_brocast_new_class(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    query = update.callback_query
    tutor = get_tutor(user_id)
    user_data = context.user_data
    # Create Class
    try:
        data = {
            "class_type": user_data['class_type'],
            "num_of_students": user_data['num_of_students'],
            "students": user_data['students'],
            "start_date": user_data['start_date'],
            "week_day": calendar.day_name[parser.parse(user_data['start_date'], dayfirst=True).weekday()] if ("E" not in str(user_data['class_type'])) else "Everyday",
            "class_time": user_data['class_time'],
            "num_classes": user_data['num_classes'],
            "course_name": user_data['course_name'],
            "parent_email": user_data['parent_email'],
            "parent_number": user_data['parent_number']
        }
        query.answer()
        class_id = create_class(data, tutor['name'])
        data = get_class(class_id)
        query.edit_message_text(
            text=format_class_details(data, class_id),
            parse_mode="Markdown"
        )
        context.bot.send_message(chat_id=user_id, text="✅ Broadcasted successfully", reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal)
    except KeyError:
        query.edit_message_text(
            text="*Token Expired. Please Try Again*",
            parse_mode="Markdown"
        )
        context.bot.send_message(chat_id=user_id, text="Main Menu", reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal)
        clear_user_data()
        return
    # Broadcast Class
    tutors = get_all_tutors()
    for tutor in tutors:
        if tutor['active'] and not tutor['admin']:
            context.bot.send_message(
                chat_id=tutor['user_id'],
                text="There are new classes available. Please check them out.",
                parse_mode="Markdown"
            )
    clear_user_data()
    return


def cancel_class_creation(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    query = update.callback_query
    user_data = context.user_data
    # Earse Data
    clear_user_data(context)
    query.answer()
    query.edit_message_text("🚫 Canceled")
    context.bot.send_message(chat_id=user_id, text="Main Menu", reply_markup=home_layout_admin if(
        tutor['admin']) else home_layout_normal)
# End of functions to add class


# Functions to surf classes
def surf(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    classes = get_tutorless_classes(user_id)
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return
    if not classes:
        context.bot.send_message(
            chat_id=user_id,
            text="No classes to show right now. Check back later"
        )
        return
    total = len(classes)
    context.bot.send_message(
        chat_id=user_id,
        text=format_surf(0, total, classes[0]),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Take Class",
                        callback_data=f"take_{classes[0]['_id']}"
                    ),

                    InlineKeyboardButton(
                        "🚫 Not Avaliable",
                        callback_data=f"leave_{classes[0]['_id']}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{'✔️ Done' if (total == 1) else 'Next ➡'}",
                        callback_data=f"next_class_{0}_{total}"
                    )
                ]
            ]
        )
    )


def next_class(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    query = update.callback_query
    text = query.data
    page = int(text.split("_")[2]) + 1
    total = int(text.split("_")[3])
    if page >= total:
        query.answer()
        query.edit_message_text("Thats all for now.")
        return
    query.edit_message_text("Loading...")
    classes = get_tutorless_classes(user_id)
    query.answer()
    query.edit_message_text(
        text=format_surf(page, total, classes[page]),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Take Class",
                        callback_data=f"take_{classes[page]['_id']}"
                    ),

                    InlineKeyboardButton(
                        "🚫 Not Avaliable",
                        callback_data=f"leave_{classes[page]['_id']}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{'✔️ Done' if (page+1 == total) else 'Next ➡'}",
                        callback_data=f"next_class_{page}_{total}"
                    )
                ]
            ]
        )
    )
# End of functions to surf classes


# Functon to show tutor classes
def my_classes(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    classes = get_user_classes(user_id)
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return
    if not classes:
        context.bot.send_message(
            chat_id=user_id,
            text="You have no classes to show"
        )
        return
    for data in classes:
        context.bot.send_message(
            chat_id=user_id,
            text=format_user_classes("ℹ️ Class Details", data),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "Send Report", callback_data=f"send_report_{data['_id']}")]
            ]) if (data['completed'] and data['report'] == "") else ""
        )
# End of functon to show tutor classes


# Functions to request to take  and leave classes
def take_class(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    query = update.callback_query
    class_id = query.data.split('_')[1]
    try:
        if get_class(class_id)['tutor']:
            query.answer()
            query.edit_message_text(
                "Sorry but this class seems to already have a tutor")
            return
    except:
        query.edit_message_text(
            "Sorry but this class does'nt seem to exist.")
        return
    assign_to_class(user_id, class_id)
    admins = get_admins()
    for admin in admins:
        context.bot.send_message(
            chat_id=admin['user_id'],
            text="They're are pending class requests."
        )
    query.answer()
    query.edit_message_text(
        "Your request to take this class has been forwarded to an admin."
    )


def leave_class(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    query = update.callback_query
    class_id = query.data.split('_')[1]
    try:
        if get_class(class_id)['tutor']:
            query.answer()
            query.edit_message_text(
                "Sorry but this class seems to already have a tutor")
            return
    except:
        query.edit_message_text(
            "Sorry but this class does'nt seem to exist.")
        return
    add_user_to_reject_list(user_id, class_id)
    query.answer()
    query.edit_message_text(
        "Alright. This class will no longer show up on your surf."
    )
# End of functions to request to take  and decline classes


# Functions to approve and decline take request
def approve_request(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    user_id = text.split("_")[1]
    class_id = text.split("_")[2]
    try:
        if get_class(class_id)['status'] != "pending":
            query.answer()
            query.edit_message_text(
                "Sorry but this class seems to already have a tutor")
            return
    except:
        query.edit_message_text(
            "Sorry but this class does'nt seem to exist.")
        return
    data = get_class(class_id)
    class_tutor = get_tutor(data['tutor'])
    approve(class_id)
    event_id = add_calander_event(data, class_tutor['email'])
    store_calendar_event_id(class_id, event_id)
    context.bot.send_message(
        chat_id=user_id,
        text="You request to take a class was *Approved*. Check your classes or Calander to see.",
        parse_mode="Markdown"
    )
    query.answer()
    query.edit_message_text("Request approved.")


def decline_request(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    user_id = text.split("_")[1]
    class_id = text.split("_")[2]
    decline(class_id)
    context.bot.send_message(
        chat_id=user_id,
        text="You request to take a class was *Declined*. Contact an admin to find out why",
        parse_mode="Markdown"
    )
    query.answer()
    query.edit_message_text("Request Declined")
# End of functions to approve and decline take request


# Function to search for db
def search(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return END
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return END
    if not tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            text="Sorry only *admins* can do that.",
            parse_mode="Markdown",
        )
        return END
    user_data['last_message_id'] = []
    user_data['last_message_id'].append(context.bot.send_message(
        chat_id=user_id,
        text="Are you looking for a *Tutor* or *Class*: ",
        parse_mode="Markdown",
        reply_markup=cancel_keybaord
    ).message_id)
    return COLLECTING_WHAT


def store_what(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['search_what'] = text
    user_data['last_message_id'].append(update.effective_message.message_id)
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text="What do you want to search by: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_BY


def invalid_what(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    user_data['last_message_id'].append(update.effective_message.message_id)
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text="*Invalid Input*. Enter *Class* or *Tutor*: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_WHAT


def store_by(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['search_by'] = text
    user_data['last_message_id'].append(update.effective_message.message_id)
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text="Enter value to search for: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_QUERY


def invalid_by(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    tutor_text = '(e.g pair\_code, tutor\_name, tutor\_email)'
    class_text = '(e.g class\_id , student\_name, course, parent\_email, parent\_number)'
    user_data['last_message_id'].append(update.effective_message.message_id)
    user_data['last_message_id'].append(
        context.bot.send_message(
            chat_id=user_id,
            text=f"*Invalid Input*. Enter a valid parameter.  {tutor_text if (user_data['search_what'] == 'Tutor') else class_text}: ",
            parse_mode="Markdown"
        ).message_id
    )
    return COLLECTING_BY


def store_query(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    user_data = context.user_data
    text = update.message.text
    user_data['last_message_id'].append(update.effective_message.message_id)
    if user_data['search_by'] == "class_id":
        if not re.match(r'(.{24})', text):
            user_data['last_message_id'].append(context.bot.send_message(
                chat_id=user_id,
                text="*Invalid Input* Enter a valid Class ID",
                parse_mode="Markdown"
            ).message_id)
            return COLLECTING_QUERY
    if user_data['search_by'] == "pair_code":
        if not re.match(r'(.{24})', text):
            user_data['last_message_id'].append(context.bot.send_message(
                chat_id=user_id,
                text="*Invalid Input* Enter a valid Pair Code",
                parse_mode="Markdown"
            ).message_id)
            return COLLECTING_QUERY
    if user_data['search_by'] == "parent_email" or user_data['search_by'] == "tutor_email":
        if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            user_data['last_message_id'].append(context.bot.send_message(
                chat_id=user_id,
                text="*Invalid Input* Enter a valid Email",
                parse_mode="Markdown"
            ).message_id)
            return COLLECTING_QUERY
    if user_data['search_by'] == "parent_number":
        if not re.match(r'^\+(?:[0-9]●?){6,14}[0-9]$', text):
            user_data['last_message_id'].append(context.bot.send_message(
                chat_id=user_id,
                text="*Invalid Input* Enter a valid Number",
                parse_mode="Markdown"
            ).message_id)
            return COLLECTING_QUERY
    user_data['search_query'] = text
    # Delete all message
    for message_id in user_data['last_message_id']:
        context.bot.delete_message(
            chat_id=user_id,
            message_id=message_id
        )
    by = ""
    query = ""
    if user_data['search_what'] == "Tutor":
        if user_data['search_by'] == "pair_code":
            by = "_id"
            query = ObjectId(user_data['search_query'])

        elif user_data['search_by'] == "tutor_name":
            by = "name"
            query = user_data['search_query']

        elif user_data['search_by'] == "tutor_email":
            by = "email"
            query = user_data['search_query']
        values = search_tutors(by, query)
        if not values:
            context.bot.send_message(
                chat_id=user_id,
                text=f"No results for *{user_data['search_query']}* in Tutors",
                reply_markup=home_layout_admin if(
                    tutor['admin']) else home_layout_normal,
                parse_mode="Markdown"
            )
            return END
        for data in values:
            context.bot.send_message(
                chat_id=user_id,
                text=format_tutor_details(data),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"{'Deactivate' if (data['active']) else 'Activate'}",
                                callback_data=f"toggle_active_{data['user_id']}"
                            ),

                            InlineKeyboardButton(
                                f"{'Remove Admin' if (data['admin']) else 'Make Admin'}",
                                callback_data=f"toggle_admin_{data['user_id']}"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "✔️ Done",
                                callback_data="done"
                            )
                        ]
                    ]
                )
            )

    else:
        if user_data['search_by'] == "class_id":
            by = "_id"
            query = ObjectId(user_data['search_query'])

        elif user_data['search_by'] == "student_name":
            by = "students"
            query = user_data['search_query']

        elif user_data['search_by'] == "course":
            by = "course_name"
            query = user_data['search_query']

        elif user_data['search_by'] == "parent_email":
            by = "parent_email"
            query = user_data['search_query']

        elif user_data['search_by'] == "parent_number":
            by = "parent_number"
            query = user_data['search_query']

        values = search_classes(by, query)
        if not values:
            context.bot.send_message(
                chat_id=user_id,
                text=f"No results for *{user_data['search_query']}* in Classes",
                reply_markup=home_layout_admin if(
                    tutor['admin']) else home_layout_normal,
                parse_mode="Markdown"
            )
            return END
        for data in values:
            context.bot.send_message(
                chat_id=user_id,
                text=format_class_details(data, data['_id'],),
                parse_mode="Markdown",
                reply_markup=decide_button(tutor, data)
            )

    context.bot.send_message(
        chat_id=user_id,
        text="Main Menu",
        reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal
    )
    return END


def toggle_tutor_active(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = int(query.data.split('_')[2])
    toggle_active(user_id)
    tutor = get_tutor(user_id)
    context.bot.send_message(
        chat_id=user_id,
        text=f"{'Hello, Your account was reactivated welcome back' if (tutor['active']) else 'Your account was just deactivated. Contact a tutor to find out why.'}",
        reply_markup=(home_layout_admin if(
            tutor['admin']) else home_layout_normal) if (
            tutor['active']) else ReplyKeyboardRemove()
    )
    query.answer()
    query.edit_message_text('Account reactivated' if (
        tutor['active']) else 'Account deactivated')


def toggle_tutor_admin(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = int(query.data.split('_')[2])
    toggle_admin(user_id)
    tutor = get_tutor(user_id)
    context.bot.send_message(
        chat_id=user_id,
        text=f"{'Hello, You are now an admin. Goodluck' if (tutor['admin']) else 'Your admin rights have been withdrawn. Goodluck'}",
        reply_markup=(home_layout_admin if(
            tutor['admin']) else home_layout_normal)
    )
    query.answer()
    query.edit_message_text('Account is now admin' if (
        tutor['admin']) else 'Account is no longer admin')


def lookup_class(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return
    try:
        class_id = context.args[0]
    except IndexError:
        context.bot.send_message(
            chat_id=user_id,
            text="You didn't pass in a class id. (e.g <get_class 123456789111234567>)",
        )
        return
    if not re.match(r'(.{24})', class_id):
        context.bot.send_message(
            chat_id=user_id,
            text="*Invalid Class ID*. Please check and retry.",
            parse_mode="Markdown"
        )
        return

    data = get_class(class_id)
    if not data:
        context.bot.send_message(
            chat_id=user_id,
            text="*Invalid Class ID*. Please check and retry.",
            parse_mode="Markdown"
        )
        return
    context.bot.send_message(
        chat_id=user_id,
        text=format_class_details(data, data['_id']) if (
            tutor['admin']) else format_user_classes("ℹ️ Class Details", data),
        parse_mode="Markdown",
        reply_markup=decide_button(tutor, data)
    )
# End of dunction to search for db


# Functions to handle reports
def collect_report(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    query = update.callback_query
    text = query.data
    user_data = context.user_data
    class_id = text.split("_")[2]
    data = get_class(class_id)
    if not data:
        query.answer()
        query.edit_message_text("Something is not right. Please try again")
        return

    if data['report']:
        query.answer()
        query.edit_message_text(
            "We already have a report for this class.")
        return
    user_data['report_class_id'] = class_id
    query.answer()
    query.delete_message()
    context.bot.send_message(
        chat_id=user_id,
        text="*Enter report for this class: *",
        parse_mode="Markdown")
    return COLLECTING_REPORT


def store_report(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    text = update.message.text
    user_data['report'] = text
    context.bot.send_message(
        chat_id=user_id,
        text=f"*ℹ️ Class Report*\n\n{text}\n\nDoes this look right?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes", callback_data="save_report"), InlineKeyboardButton(
                "🚫 Cancel", callback_data="discard_report")]
        ])
    )
    return END


def save_report(update: Update, context: CallbackContext):
    query = update.callback_query
    user_data = context.user_data
    class_id = user_data['report_class_id']
    report = user_data['report']
    admins = get_admins()
    submit_report(class_id, report)
    for admin in admins:
        context.bot.send_message(
            chat_id=admin['user_id'],
            text=f"A report was send in. run (`/get_class {class_id}`) to view.",
            parse_mode="Markdown"
        )
    query.answer()
    query.edit_message_text("Report Sent Successfully.")


def discard_report(update: Update, context: CallbackContext):
    query = update.callback_query
    user_data = context.user_data
    user_data['report_class_id'] = ""
    user_data['report'] = ""
    query.answer()
    query.edit_message_text("🚫 Canceled")


def show_report(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    class_id = text.split("_")[2]
    data = get_class(class_id)
    if not data:
        query.answer()
        query.edit_message_text("Something is not right. Please try again")
        return

    if not data['report']:
        query.answer()
        query.edit_message_text("No report for this class.")
        return
    query.answer()
    query.edit_message_text(
        f"*ℹ️ Class Report*\n\n{data['report']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "⬅ Back", callback_data=f"back_to_class_{data['_id']}")]
        ])
    )


def back_to_class(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    tutor = get_tutor(user_id)
    query = update.callback_query
    text = query.data
    class_id = text.split("_")[3]
    data = get_class(class_id)
    if not data:
        query.answer()
        query.edit_message_text("Something is not right. Please try again")
        return
    query.answer()
    query.edit_message_text(
        text=format_class_details(data, data['_id']) if (
            tutor['admin']) else format_user_classes("ℹ️ Class Details", data),
        parse_mode="Markdown",
        reply_markup=decide_button(tutor, data)
    )


def request_report(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    class_id = text.split("_")[2]
    data = get_class(class_id)
    if not data:
        query.answer()
        query.edit_message_text("Something is not right. Please try again")
        return

    if data['report']:
        query.answer()
        query.edit_message_text(
            "We already have a report for this class. If it doesnt look right please clear it before requesting anthoer.")
        return
    context.bot.send_message(
        chat_id=data['tutor'],
        text=format_user_classes("ℹ️ Report Request", data),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Send Report", callback_data=f"send_report_{data['_id']}")]
        ]) if (data['completed'] and data['report'] == "") else ""
    )
    query.answer()
    query.edit_message_text("Report Request sent.")


def remove_report(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    class_id = text.split("_")[2]
    data = get_class(class_id)
    if not data:
        query.answer()
        query.edit_message_text("Something is not right. Please try again")
        return
    if not data['report']:
        query.answer()
        query.edit_message_text("No report for this class.")
        return
    delete_report(class_id)
    context.bot.send_message(
        chat_id=data['tutor'],
        text="Hello, A report you send was rejected. Please follow reporting guilds to create the perfect class report",
    )
    data = get_class(class_id)
    context.bot.send_message(
        chat_id=data['tutor'],
        text=format_user_classes("ℹ️ Report Request", data),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Send Report", callback_data=f"send_report_{data['_id']}")]
        ])
    )
    query.answer()
    query.edit_message_text("Report deleted and Request has been sent.")


def end_session(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    class_id = text.split("_")[2]
    data = get_class(class_id)
    if not data:
        query.answer()
        query.edit_message_text("Something is not right. Please try again")
        return
    if not data['tutor']:
        query.answer()
        query.edit_message_text("This class does not have a tutor.")
        return
    if data['completed']:
        query.answer()
        query.edit_message_text("This class has already ended.")
        return
    end_class_session(class_id)
    delete_calendar_event(data['event_id'])
    data = get_class(class_id)
    context.bot.send_message(
        chat_id=data['tutor'],
        text=format_user_classes("ℹ️ Class Ended", data),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Send Report", callback_data=f"send_report_{data['_id']}")]
        ])
    )
    query.answer()
    query.edit_message_text("Class ended. Now awaiting report.")
# End of functions to handle reports


# Functions to edit class details
def change_class_details(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    query = update.callback_query
    text = query.data
    class_id = text.split("_")[2]
    data = get_class(class_id)
    if not data:
        query.answer()
        query.edit_message_text("Something is not right. Please try again")
        return
    user_data['old_class_details'] = data
    # make sure to ask if can still take class
    user_data['do_not_ask'] = False
    query.answer()
    query.delete_message()
    user_data['last_message_id'] = []
    user_data['last_message_id'].append(context.bot.send_message(
        chat_id=user_id,
        text=f"Enter Class Type or `{user_data['old_class_details']['class_type']}`",
        parse_mode="Markdown",
        reply_markup=cancel_keybaord
    ).message_id)
    return COLLECTING_CLASS_TYPE


def submit_edit(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    query = update.callback_query
    tutor = get_tutor(user_id)
    user_data = context.user_data
    try:
        old_class = user_data['old_class_details']
        data = {
            "class_type": user_data['class_type'],
            "num_of_students": user_data['num_of_students'],
            "students": user_data['students'],
            "start_date": user_data['start_date'],
            "week_day": calendar.day_name[parser.parse(user_data['start_date'], dayfirst=True).weekday()] if ("E" not in str(user_data['class_type'])) else "Everyday",
            "class_time": user_data['class_time'],
            "num_classes": user_data['num_classes'],
            "course_name": user_data['course_name'],
            "parent_email": user_data['parent_email'],
            "parent_number": user_data['parent_number']
        }
        query.answer()
        if user_data['do_not_ask']:
            submit_new_class_details(
                old_class['_id'], data, old_class['status'])
        else:
            submit_new_class_details(old_class['_id'], data, "tentative")
        data = get_class(old_class['_id'])
        query.edit_message_text(
            text=format_class_details(data, old_class['_id']),
            parse_mode="Markdown"
        )
        context.bot.send_message(
            chat_id=user_id,
            text="Main Menu",
            reply_markup=home_layout_admin if(
                tutor['admin']) else home_layout_normal)
        # if not to ask
        if user_data['do_not_ask']:
            return END
        context.bot.send_message(
            chat_id=data['tutor'],
            text=format_edit_user_classes(
                "ℹ️ Editted Class Details", data, old_class),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✅ Yes",
                            callback_data=f"still_available_{old_class['_id']}"
                        ),
                        InlineKeyboardButton(
                            "🚫 No",
                            callback_data=f"not_available_{old_class['_id']}"
                        )
                    ]
                ]
            )
        )
    except KeyError:
        query.edit_message_text(
            text="*Token Expired. Please Try Again*",
            parse_mode="Markdown"
        )
        context.bot.send_message(chat_id=user_id, text="Main Menu", reply_markup=home_layout_admin if(
            tutor['admin']) else home_layout_normal)
        return


def still_available(update: Update, context: CallbackContext):
    query = update.callback_query
    class_id = query.data.split('_')[2]
    data = get_class(class_id)
    if not data:
        query.answer()
        query.edit_message_text("Something is not right. Please try again")
        return
    if data['status'] != "tentative":
        query.answer()
        query.edit_message_text("You seem to have done this before.")
        return
    accept_editted_class(data)
    admins = get_admins()
    for admin in admins:
        context.bot.send_message(
            chat_id=admin['user_id'],
            text="They're are pending class requests."
        )

    query.edit_message_text(
        "Your request to still take this class has been forwarded to an admin."
    )


def not_available(update: Update, context: CallbackContext):
    query = update.callback_query
    class_id = query.data.split('_')[2]
    data = get_class(class_id)
    if not data:
        query.answer()
        query.edit_message_text("Something is not right. Please try again")
        return
    if data['status'] != "tentative":
        query.answer()
        query.edit_message_text("You seem to have done this before.")
        return
    decline_editted_class(data)
    query.answer()
    query.edit_message_text(
        "Alright this class will be opened to other tutor."
    )


def edit_class(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    user_data = context.user_data
    tutor = get_tutor(user_id)
    if not tutor:
        context.bot.send_message(
            chat_id=user_id,
            text="👋 *Hi There Stranger*, use the /connect command to link your account.",
            parse_mode="Markdown"
        )
        return END
    if not tutor['active']:
        context.bot.send_message(
            chat_id=user_id,
            text=f"👋 *Hi {tutor['name']}*, your account has been disabled please contact an admin",
            parse_mode="Markdown"
        )
        return END
    if not tutor['admin']:
        context.bot.send_message(
            chat_id=user_id,
            text="Sorry only *admins* can do that.",
            parse_mode="Markdown",
        )
        return END
    try:
        class_id = context.args[0]
    except IndexError:
        context.bot.send_message(
            chat_id=user_id,
            text="You didn't pass in a class id. (e.g <edit_class 123456789111234567>)",
        )
        return END
    if not re.match(r'(.{24})', class_id):
        context.bot.send_message(
            chat_id=user_id,
            text="*Invalid Class ID*. Please check and retry.",
            parse_mode="Markdown"
        )
        return END
    data = get_class(class_id)
    if not data:
        context.bot.send_message(
            chat_id=user_id,
            text="*Invalid Class ID*. Please check and retry.",
            parse_mode="Markdown"
        )
        return END
    if data['status'] != "pending" and data['status'] != "tentative":
        context.bot.send_message(
            chat_id=user_id,
            text="*Warning* You seem to be editing a class in progress.",
            parse_mode="Markdown"
        )
    user_data['old_class_details'] = data
    # Makes sure bot doesnt tell about changes
    user_data['do_not_ask'] = True
    user_data['last_message_id'] = []
    user_data['last_message_id'].append(context.bot.send_message(
        chat_id=user_id,
        text=f"Enter Class Type or `{user_data['old_class_details']['class_type']}`",
        parse_mode="Markdown",
        reply_markup=cancel_keybaord
    ).message_id)
    return COLLECTING_CLASS_TYPE


# Handler for all done buttons
def done(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    query = update.callback_query
    query.answer()
    query.delete_message()
    context.bot.send_message(
        chat_id=user_id,
        text="Main Menu"
    )


def main():
    # creating a dispatcher
    updater = Updater(token="5221408101:AAHBv-TngqeSVzYTkaisRPTdW_Mc3MqyALw")

    dispatcher = updater.dispatcher

    # handlers
    start_handler = CommandHandler('start', start)
    lookup_handler = CommandHandler('get_class', lookup_class)
    create_tutor_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create_tutor), MessageHandler(
            Filters.regex(r'Add Tutor'), create_tutor), ],
        states={
            COLLECTING_NAME: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(
                    r"^([a-zA-Z]{2,}\s[a-zA-Z]{1,}'?-?[a-zA-Z]{2,}\s?([a-zA-Z]{1,})?)"), store_name),
                MessageHandler(Filters.text & (~Filters.command), invalid_name)
            ],
            COLLECTING_EMAIL: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), store_email),
                MessageHandler(Filters.text & (
                    ~Filters.command), invalid_email)
            ],
        },
        fallbacks=[MessageHandler(Filters.text & (~Filters.command), echo)]
    )
    pair_tutor_handler = ConversationHandler(
        entry_points=[CommandHandler("connect", connect_account)],
        states={
            COLLECTING_CODE: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(
                    r"[0-9a-zA-Z]{24}"), link_code),
                MessageHandler(Filters.text & (
                    ~Filters.command), invalid_code)
            ]
        },
        fallbacks=[MessageHandler(Filters.text & (~Filters.command), echo)]
    )
    user_keyboard_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex(r"Surf Classes"), surf),
            MessageHandler(Filters.regex(r"My Classes"), my_classes),
            CommandHandler("surf", surf),
            CommandHandler("my_classes", my_classes),
        ],
        states={},
        fallbacks=[MessageHandler(Filters.text & (~Filters.command), echo)]
    )
    admin_keyboard_button_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex(r"Help"), help),
            MessageHandler(Filters.regex(r"🏠 Main Menu"), main_menu),
            MessageHandler(Filters.regex(r"Pending"), show_pending),
            MessageHandler(Filters.regex(r"Export Classes"), show_classes),
            MessageHandler(Filters.regex(r"Add Class"), add_class),
            MessageHandler(Filters.regex(r"Export Tutors"), show_tutors),
            MessageHandler(Filters.regex(r"Tutors"), tutor_menu),
            MessageHandler(Filters.regex(r"Classes"), class_menu),
            CallbackQueryHandler(
                change_class_details, pattern=r"change_details_(.{24})"),
            CommandHandler('add_class', add_class),
            CommandHandler('edit_class', edit_class),
        ],
        states={
            COLLECTING_CLASS_TYPE: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(r"PT|VG|PT-E|VG-E"), store_type),
                MessageHandler(Filters.text & (
                    ~Filters.command), invalid_type)
            ],
            COLLECTING_NUMBER_OF_STUNDETS: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(r"\d"), store_number_of_students),
                MessageHandler(Filters.text & (
                    ~Filters.command), invalid_number)
            ],
            COLLECTING_STUDENT_NAME: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.text & (
                    ~Filters.command), store_student_names)
            ],
            COLLECTING_START_DATE: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(
                    r"^([0]?[1-9]|[1|2][0-9]|[3][0|1])[-]([0]?[1-9]|[1][0-2])[-]([0-9]{4})$"), store_start_date),
                MessageHandler(Filters.text & (
                    ~Filters.command), invalid_start_date)
            ],
            COLLECTING_TIME: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(
                    r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$"), store_class_time),
                MessageHandler(Filters.text & (
                    ~Filters.command), invalid_class_time)
            ],
            COLLECTING_NUMBER_OF_CLASSES: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(r"\d"), store_num_classes),
                MessageHandler(Filters.text & (
                    ~Filters.command), invalid_num_classes)
            ],
            COLLECTING_COURSE_NAME: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.text & (
                    ~Filters.command), store_course_name)
            ],
            COLLECTING_PARENTS_EMAIL: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.text & (
                    ~Filters.command), store_parent_email),
            ],
            COLLECTING_PARENTS_NUMBER: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.text & (
                    ~Filters.command), store_parent_number),
            ]
        },
        fallbacks=[MessageHandler(Filters.text & (~Filters.command), echo)]
    )
    search_handler = ConversationHandler(
        entry_points=[
            CommandHandler('search', search),
        ],
        states={
            COLLECTING_WHAT: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(r"Tutor|Class"), store_what),
                MessageHandler(Filters.text & (
                    ~Filters.command), invalid_what)
            ],
            COLLECTING_BY: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.regex(
                    r"class_id|student_name|course|parent_email|parent_number|tutor_name|tutor_email|pair_code"), store_by),
                MessageHandler(Filters.text & (
                    ~Filters.command), invalid_by)
            ],
            COLLECTING_QUERY: [
                MessageHandler(Filters.regex(r'🚫 Cancel'), cancel),
                MessageHandler(Filters.text & (
                    ~Filters.command), store_query)
            ]
        },
        fallbacks=[MessageHandler(Filters.text & (~Filters.command), echo)]
    )
    report_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            collect_report, pattern=r"send_report_(.{24})")],
        states={
            COLLECTING_REPORT: [
                MessageHandler(Filters.text & (
                    ~Filters.command), store_report)
            ]
        },
        fallbacks=[MessageHandler(Filters.text & (~Filters.command), echo)],
    )
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    create_new_class_handler = CallbackQueryHandler(
        create_new_class, pattern="create_class")
    create_broadcast_handler = CallbackQueryHandler(
        create_brocast_new_class, pattern="create_broadcast")
    cancel_class_creation_handler = CallbackQueryHandler(
        cancel_class_creation, pattern="cancel_class_creation")
    next_class_handler = CallbackQueryHandler(
        next_class, pattern=r"next_class_(\d*)_(\d*)")
    take_class_handler = CallbackQueryHandler(
        take_class, pattern=r"take_(.{24})")
    leave_class_handler = CallbackQueryHandler(
        leave_class, pattern=r"leave_(.{24})")
    approve_request_handler = CallbackQueryHandler(
        approve_request, pattern=r"approve_(.*)_(.*)")
    decline_request_handler = CallbackQueryHandler(
        decline_request, pattern=r"decline_(.*)_(.*)")
    toggle_tutor_active_handler = CallbackQueryHandler(
        toggle_tutor_active, pattern=r"toggle_active_(\d*)")
    toggle_tutor_admin_handler = CallbackQueryHandler(
        toggle_tutor_admin, pattern=r"toggle_admin_(\d*)")
    done_handler = CallbackQueryHandler(
        done, pattern="done")
    save_report_handler = CallbackQueryHandler(
        save_report, pattern="save_report")
    discard_report_handler = CallbackQueryHandler(
        discard_report, pattern="discard_report")
    show_report_handler = CallbackQueryHandler(
        show_report, pattern=r"show_report_(.{24})")
    request_report_handler = CallbackQueryHandler(
        request_report, pattern=r"request_report_(.{24})")
    remove_report_handler = CallbackQueryHandler(
        remove_report, pattern=r"remove_report_(.{24})")
    end_session_handler = CallbackQueryHandler(
        end_session, pattern=r"end_session_(.{24})")
    back_to_class_handler = CallbackQueryHandler(
        back_to_class, pattern=r"back_to_class_(.{24})")
    submit_edit_handler = CallbackQueryHandler(
        submit_edit, pattern=r"submit_edit")
    still_available_handler = CallbackQueryHandler(
        still_available, pattern=r"still_available_(.{24})")
    not_available_handler = CallbackQueryHandler(
        not_available, pattern=r"not_available_(.{24})")

   # dispatchers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(create_tutor_handler)
    dispatcher.add_handler(pair_tutor_handler)
    dispatcher.add_handler(user_keyboard_handler)
    dispatcher.add_handler(admin_keyboard_button_handler)
    dispatcher.add_handler(search_handler)
    dispatcher.add_handler(report_handler)
    dispatcher.add_handler(create_new_class_handler)
    dispatcher.add_handler(create_broadcast_handler)
    dispatcher.add_handler(cancel_class_creation_handler)
    dispatcher.add_handler(next_class_handler)
    dispatcher.add_handler(take_class_handler)
    dispatcher.add_handler(leave_class_handler)
    dispatcher.add_handler(approve_request_handler)
    dispatcher.add_handler(decline_request_handler)
    dispatcher.add_handler(toggle_tutor_active_handler)
    dispatcher.add_handler(toggle_tutor_admin_handler)
    dispatcher.add_handler(done_handler)
    dispatcher.add_handler(lookup_handler)
    dispatcher.add_handler(save_report_handler)
    dispatcher.add_handler(discard_report_handler)
    dispatcher.add_handler(show_report_handler)
    dispatcher.add_handler(request_report_handler)
    dispatcher.add_handler(remove_report_handler)
    dispatcher.add_handler(end_session_handler)
    dispatcher.add_handler(back_to_class_handler)
    dispatcher.add_handler(submit_edit_handler)
    dispatcher.add_handler(still_available_handler)
    dispatcher.add_handler(not_available_handler)

    # must be at the bottom for when here are no ongoing convos
    dispatcher.add_handler(echo_handler)

    # start pollings
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
