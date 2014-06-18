import requests
import json
from celery.decorators import task
from mxit.client import Mxit
from django.conf import settings
from mama.utils import mobile_number_to_international


@task
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

@task
def send_mxit_message(username, msg):
    """ Send a mxit message to a single user """
    client = Mxit(settings.MXIT_CLIENT_ID,
                  settings.MXIT_CLIENT_SECRET,
                  settings.MXIT_MOBI_PORTAL_URL)

    app_id = settings.MXIT_APP_ID
    client.messaging.send_message(app_id, [username], msg)
