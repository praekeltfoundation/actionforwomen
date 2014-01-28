from django.conf import settings
import requests
import json


def mobile_number_to_international(mobile_number):
    if mobile_number.startswith('0') and len(mobile_number) == 10:
            mobile_number = '27' + mobile_number[1:]
    return mobile_number


def send_sms(to_msisdn, msg):
    url = 'https://go.vumi.org/api/v1/go/http_api_nostream/%s/messages.json' % (
        settings.VUMI_SMS_CONVERSATION_KEY
    )

    data = {
        "content": msg,
        "to_addr": mobile_number_to_international(to_msisdn)
    }
    requests.put(
        url,
        json.dumps(data),
        auth=(settings.VUMI_ACCOUNT_KEY, settings.VUMI_ACCESS_TOKEN),
    )
