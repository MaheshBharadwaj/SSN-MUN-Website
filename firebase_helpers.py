from typing import final
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
firestore_db = firestore.client()

# message_obj = {
#         "message-id": None,
#         "send-del-id": send_delegate_id,
#         "send-del-country": send_delegate_country,
#         "recv-del-id": recv_delegate_id,
#         "recv-del-country": recv_delegate_country,
#         "substantiative": substantiative_check,
#         "timestamp": time.time(),
#         "message": message,
#         "to-eb": to_eb,
#         "parent": None,
#     }


def send_delegate(message_obj: dict):
    """
        Handles send and receive of messages through the database
    """
    committee = message_obj["send-del-id"][:2]
    sender_id = message_obj["send-del-id"][2:]
    receiver_id = message_obj["recv-del-id"][2:]
    try:
        sender_existing_array = (
            firestore_db.collection(committee).document(sender_id).get().to_dict()
        )
        sender_existing_array["sent_count"] += 1
        message_obj["message-id"] = sender_id + "-" + str(sender_existing_array["sent_count"])  #For identifying unique message objects
        sender_existing_array["sent_messages"].append(message_obj)
        receiver_existing_array = (
            firestore_db.collection(committee).document(receiver_id).get().to_dict()
        )
        receiver_existing_array["recv_count"] += 1
        receiver_existing_array["recv_messages"].append(message_obj)

        if message_obj["to-eb"]:
            eb_existing_array = (
                firestore_db.collection(committee).document("EB").get().to_dict()
            )
            eb_existing_array["recv_count"] += 1
            eb_existing_array["recv_messages"].append(message_obj)

        firestore_db.collection(committee).document(sender_id).set(
            sender_existing_array
        )
        firestore_db.collection(committee).document(receiver_id).set(
            receiver_existing_array
        )
        if message_obj["to-eb"]:
            firestore_db.collection(committee).document("EB").set(eb_existing_array)

    except Exception as e:
        print("Exception: " + str(e))

def send_eb(message_obj : dict):
    committee = message_obj["send-del-id"][:2]
    sender_id = message_obj["send-del-id"][2:]
    receiver_id = "EB"
    try:
        sender_existing_array = (
            firestore_db.collection(committee).document(sender_id).get().to_dict()
        )
        sender_existing_array["sent_count"] += 1
        message_obj["message-id"] = sender_id + "-" + str(sender_existing_array["sent_count"])  #For identifying unique message objects
        sender_existing_array["sent_messages"].append(message_obj)

        
        eb_existing_array = (
            firestore_db.collection(committee).document("EB").get().to_dict()
        )
        eb_existing_array["recv_count"] += 1
        eb_existing_array["recv_messages"].append(message_obj)

        firestore_db.collection(committee).document(sender_id).set(
            sender_existing_array
        )
        firestore_db.collection(committee).document("EB").set(eb_existing_array)

    except Exception as e:
        print("Exception: " + str(e))

# def check_recved(user_id):
#     committee = user_id[:2]
#     id = user_id[2:]

#     data = firestore_db.collection(committee).document(id).get().to_dict()
#     recv_count = data["recv_count"]

#     return recv_count

def get_sent_messages(user_id):
    committee = user_id[:2]
    id = user_id[2:]

    data = firestore_db.collection(committee).document(id).get().to_dict()

    sent_messages = data["sent_messages"]

    return sent_messages

def get_recv_messages(user_id):
    committee = user_id[:2]
    id = user_id[2:]

    data = firestore_db.collection(committee).document(id).get().to_dict()

    recv_messages = data["recv_messages"]

    return recv_messages