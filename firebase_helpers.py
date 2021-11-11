from typing import final
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
firestore_db = firestore.client()

# message_obj = {
#         'parent': None
#         'send-del-id': send_delegate_id,
#         'send-del-country': send_delegate_country,
#         'recv-del-id': recv_delegate_id,
#         'recv-del-country': recv_delegate_country,
#         'substantiative': substantiative_check,
#         'timestamp': time.time(),
#         'message': message,
#         'to-eb': to_eb
#     }


def send_delegate(message_obj: dict):
    committee = message_obj["send-del-id"][:2]
    sender_id = message_obj["send-del-id"][2:]
    receiver_id = message_obj["recv-del-id"][2:]
    try:
        sender_existing_array = (
            firestore_db.collection(committee).document(sender_id).get().to_dict()
        )
        sender_existing_array["sent_count"] += 1
        sender_existing_array["sent_messages"].append(message_obj)
        recevier_existing_array = (
            firestore_db.collection(committee).document(receiver_id).get().to_dict()
        )
        recevier_existing_array["recv_count"] += 1
        recevier_existing_array["recv_messages"].append(message_obj)

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
            recevier_existing_array
        )
        if message_obj["to-eb"]:
            firestore_db.collection(committee).document("EB").set(eb_existing_array)

    except Exception as e:
        print("Exception: " + str(e))
