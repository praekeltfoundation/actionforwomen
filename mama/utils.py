from mxit.client import Mxit


def mobile_number_to_international(mobile_number):
    if mobile_number.startswith('0') and len(mobile_number) == 10:
            mobile_number = '27' + mobile_number[1:]
    return mobile_number

# ----------------------------------------------------------------

#MXIT STAGED BASED MESSAGING
# The Mxit API has changed significantly over the past 3 months


def send_message(client_id, client_secret, app_uri, app_id, users, message):

    # client_id : Client Id from Mxit
    # client_secret : Secret from Mxit
    # app_uri : Mobi Portal Url from Mxit
    # app_id :  App Mxit ID from Mxit

    # users: List of users []
    # message: Message to send


    client = Mxit(client_id, client_secret, redirect_uri=app_uri)
    client.messaging.send_message(app_id, users, message)

    # send_message("83b677c8819c4dc091663336926296ee", "a3adb462d8214e90a7de55c1cb6cac91", "http://juizi.dyndns.org:8001/", "avu_juizi", ['m56653879002'], "This is a test message")
