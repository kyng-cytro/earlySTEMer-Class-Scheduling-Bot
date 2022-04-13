from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
from csv import writer

client = MongoClient(
    "mongodb+srv://cytro:hXFtGARhZbPRyT8h@earlystemer.ezebs.mongodb.net/bot_db?retryWrites=true&w=majority"
)

db = client.bot_db


# Creates tutor and return pair id
def create_new_tutor(name, email, admin):
    tutors = db.tutors
    pair_id = tutors.insert_one({
        "user_id": "",
        "name": name,
        "email": email,
        "admin": False,
        "active": False,
        "created_by": admin,
        "create_date": datetime.now(),
        "modified_date": datetime.now()
    }).inserted_id
    return pair_id


# Checks if pair_id is valid
def check_pair_id(pair_id):
    tutors = db.tutors
    data = tutors.find_one({'_id': ObjectId(pair_id)})
    if not data:
        return False
    if data['user_id']:
        return False
    return True


# Pairs user_id to tutor account
def pair_tutor(user_id, pair_id):
    tutors = db.tutors
    try:
        tutors.update_one(
            {"_id": ObjectId(pair_id)},
            {"$set": {
                'user_id': user_id,
                "active": True,
                "modified_date": datetime.now()
            }
            }
        )
        return True
    except:
        return False


# Get tutor's account by id
def get_tutor(user_id):
    tutors = db.tutors
    return tutors.find_one({'user_id': user_id})


# Get all tutors
def get_all_tutors():
    tutors = db.tutors
    return list(tutors.find({}))


def get_admins():
    tutors = db.tutors
    return list(tutors.find({"admin": True}))


# Creates new class
def create_class(data, admin):
    classes = db.classes
    class_id = classes.insert_one({
        "class_type": data['class_type'],
        "num_of_students": data['num_of_students'],
        "students": data['students'],
        "start_date": data['start_date'],
        "week_day": data['week_day'],
        "class_time": data['class_time'],
        "num_classes": data['num_classes'],
        "course_name": data['course_name'],
        "parent_email": data['parent_email'],
        "parent_number": data['parent_number'],
        "tutor": "",
        "report": "",
        "completed": False,
        "status": "tentative",
        "created_by": admin,
        "create_date": datetime.now(),
        "modified_date": datetime.now()
    }).inserted_id

    return class_id


# Get a class by id
def get_class(class_id):
    classes = db.classes
    return classes.find_one({'_id': ObjectId(class_id)})


# Get all classes
def get_all_classes():
    classes = db.classes
    return list(classes.find({}))


def get_tutorless_classes(user_id):
    classes = db.classes
    total = []
    chunk = list(classes.find({}))
    for data in chunk:
        if not data['tutor']:
            try:
                for reject in data['rejects']:
                    if reject == user_id:
                        continue
                    total.append(data)
            except KeyError:
                total.append(data)
    return total


def get_user_classes(user_id):
    classes = db.classes
    return list(classes.find({"tutor": user_id}))


def get_pending_classes():
    classes = db.classes
    return list(classes.find({"status": "pending"}))


# Get all classes , creates a csv and returns the path
def csv_classes():
    classes = db.classes
    chunk = classes.find({})
    filepath = f"csv/classes/{datetime.now():%Y_%m_%d}.csv"
    with open(filepath, 'w', newline='') as csvfile:
        writer_object = writer(csvfile)
        writer_object.writerow([
            "class_ID",
            "class_type",
            "num_of_students",
            "students",
            "start_date",
            "week_day",
            "class_time",
            "num_classes",
            "course_name",
            "parent_email",
            "parent_number",
            "tutor",
            "status",
            "created_by",
            "create_date",
            "modified_date"
        ])
        for data in chunk:
            writer_object.writerow([
                data['_id'],
                data["class_type"],
                data["num_of_students"],
                data["students"],
                data["start_date"],
                data["week_day"],
                data["class_time"],
                data["num_classes"],
                data["course_name"],
                data['parent_email'],
                data['parent_number'],
                data["tutor"],
                data["status"],
                data["created_by"],
                data["create_date"],
                data["modified_date"]
            ])
    return filepath


# Get all tutors , creates a csv and returns the path
def csv_tutors():
    tutors = db.tutors
    chunk = tutors.find({})
    filepath = f"csv/tutors/{datetime.now():%Y_%m_%d}.csv"
    with open(filepath, 'w', newline='') as csvfile:
        writer_object = writer(csvfile)
        writer_object.writerow([
            "pair_code",
            "user_id",
            "name",
            "email",
            "admin",
            "active",
            "created_by",
            "create_date",
            "modified_date"
        ])
        for data in chunk:
            writer_object.writerow([
                data['_id'],
                data["user_id"],
                data["name"],
                data["email"],
                data["admin"],
                data["active"],
                data["created_by"],
                data["create_date"],
                data["modified_date"]
            ])
    return filepath


# adds a tutor to the class and changes status
def assign_to_class(user_id, class_id):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {"$set":
            {"tutor": user_id,
             "status": "pending",
             "modified_date": datetime.now()
             },
         }
    )


# add user to list of people not show class
def add_user_to_reject_list(user_id, class_id):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {
            "$addToSet": {
                "rejects": user_id
            }
        }
    )


def approve(class_id):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {"$set":
            {
                "status": "ongoing",
                "modified_date": datetime.now()
            },
         }
    )


def decline(class_id):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {"$set":
            {"tutor": "",
             "status": "tentative",
             "modified_date": datetime.now()
             },
         }
    )


def search_tutors(by, query):
    tutors = db.tutors
    try:
        return list(tutors.find({by: {"$regex": rf'{query}', "$options": 'i'}}))
    except KeyError:
        return []


def search_classes(by, query):
    classes = db.classes
    try:
        return list(classes.find({by: {"$regex": rf'{query}', "$options": 'i'}}))
    except KeyError:
        return []


def toggle_active(user_id):
    tutors = db.tutors
    tutors.find_one_and_update(
        {"user_id": user_id},
        [
            {"$set":
             {
                 "active": {"$not": "$active"},
                 "modified_date": datetime.now()
             }
             }
        ]
    )


def toggle_admin(user_id):
    tutors = db.tutors
    tutors.find_one_and_update(
        {"user_id": user_id},
        [
            {"$set":
             {
                 "admin": {"$not": "$admin"},
                 "modified_date": datetime.now()
             }
             }
        ]
    )


def submit_report(class_id, report):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {"$set":
         {
             "report": report,
             "status": "completed",
             "modified_date": datetime.now()
         }
         }

    )


def delete_report(class_id):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {"$set":
         {
             "report": "",
             "status": "awaiting report",
             "modified_date": datetime.now()
         }
         }

    )


def end_class_session(class_id):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {"$set":
         {
             "completed": True,
             "status": "awaiting report",
             "modified_date": datetime.now()
         }
         }
    )


def submit_new_class_details(class_id, data, status):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {"$set":
         {
             "class_type": data['class_type'],
             "num_of_students": data['num_of_students'],
             "students": data['students'],
             "start_date": data['start_date'],
             "week_day": data['week_day'],
             "class_time": data['class_time'],
             "num_classes": data['num_classes'],
             "course_name": data['course_name'],
             "parent_email": data['parent_email'],
             "parent_number": data['parent_number'],
             "status": status,
             "modified_date": datetime.now()
         }
         }
    )


def accept_editted_class(data):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(data['_id'])},
        {"$set":
         {
             "status": "pending",
             "modified_date": datetime.now()
         }
         }
    )


def decline_editted_class(data):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(data['_id'])},
        {"$set":
         {
             "tutor": "",
             "modified_date": datetime.now()
         }
         }
    )


def store_calendar_event_id(class_id, event_id):
    classes = db.classes
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {
            "$set": {
                "event_id": event_id,
                "modified_date": datetime.now()
            }
        }
    )
