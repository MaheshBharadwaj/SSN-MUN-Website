import firebase_admin
from firebase_admin import credentials, firestore



def main():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    firestore_db = firestore.client()



    committees = ['HR', 'SC', 'OR', 'SF']
    # committees = ['HR']

    for committee in committees:
        # for i in range(1, 800):
        #     idx = str(i)
        #     while len(idx) < 3:
        #         idx = "0" + idx

        #     firestore_db.collection(committee).document(idx).set({'recv_count': 0, 'recv_messages': [], 'sent_count': 0, 'sent_messages': []})
        firestore_db.collection(committee).document(committee + "EB").set({'recv_count': 0, 'recv_messages': [], 'sent_count': 0, 'sent_messages': []})
    snapshots = list(firestore_db.collection(u"HR").get())
    for snapshot in snapshots:
        print(snapshot.to_dict())


if __name__ == "__main__":
    print('This script deletes and resets all messages. Do you want to proceed 1/0: ', end='')
    opt = int(input())
    if opt == 1:
        main()
    else:
        pass