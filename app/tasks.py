import requests
import json
from celery.decorators import task
from datetime import date, timedelta
from django.conf import settings
from app.utils import mobile_number_to_international, unban_user


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


def unban_users():
    from django.contrib.auth.models import User
    banned_users = User.objects.filter(userprofile__banned=True)

    for user in banned_users:
        if not user.profile.ban_duration or not user.profile.last_banned_date:
            continue

        unban_date = user.profile.last_banned_date + timedelta(days=user.profile.ban_duration)
        if unban_date <= date.today():
            unban_user(user)
