from celery.decorators import task
from celery.utils.log import get_task_logger
from django.conf import settings
import requests
import xmltodict, json
from datetime import datetime, timedelta
from monitor.custom_exceptions import TokenInvalidError, TokenExpireError, RechargeException
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives


logger = get_task_logger(__name__)


@task
def run_tasks():
    chain = hotsocket_login.s() | status_query.s()
    chain()


@task
def hotsocket_login():
    data = {
                "username": settings.HOTSOCKET_USERNAME,
                "password": settings.HOTSOCKET_PASSWORD,
                "as_json": True
            }

    url = "%s%s" % (settings.HOTSOCKET_BASE, settings.HOTSOCKET_RESOURCES["login"])
    response = requests.post(url, data=data)
    json_response = response.json()
    if str(json_response["response"]["status"]) == "0000":
        return json_response["response"]["token"]
    return None

@task
def status_query(token):
    """
    Recharges
    """
    if token:
        url = "%s%s" % (settings.HOTSOCKET_BASE, settings.HOTSOCKET_RESOURCES["statement"])
        code = settings.HOTSOCKET_CODES
        try:
            now = datetime.now()
            yesterday = now - timedelta(hours=240)
            data = {"username": settings.HOTSOCKET_USERNAME,
                    "token": token,
                    "start_date": yesterday.strftime("%Y-%m-%d"),
                    "end_date": now.strftime("%Y-%m-%d"),
                    "as_json": True}

            response = requests.post(url, data=data)

            if "text/xml" in response.headers["content-type"]:
                json_response = xml_to_json(response)
            elif "application/json" in response.headers["content-type"]:
                json_response = response.json()

            status = json_response["response"]["status"]
            message = json_response["response"]["message"]

            if str(status) == str(code["SUCCESS"]["status"]):
                failures = [d for d in json_response["response"]["line_item"] if d["status_desc"] != "SUCCESS"]
                email_errors(failures)

            elif status == code["TOKEN_EXPIRE"]["status"]:
                raise TokenExpireError(message)

            elif status == code["TOKEN_INVALID"]["status"]:
                raise TokenInvalidError(message)

        except (TokenInvalidError, TokenExpireError), exc:
                    status_query.retry(args=[hotsocket_login.delay().get()], exc=exc)
    else:
        raise RechargeException("No Token was found make sure hotsocket api is up")


def xml_to_json(response):
    parse_xml = xmltodict.parse(response.content)
    xml_to_json = json.dumps(parse_xml)
    return json.loads(xml_to_json)


def email_errors(failures):
    plain_template = get_template('email_failures.txt')
    html_template = get_template('email_failures.html')
    data = Context({ 'failures': failures })
    subject, from_email, to = 'hello', settings.SENDER, 'to@example.com'
    text_content = plain_template.render(data)
    html_content = html_template.render(data)

    msg = EmailMultiAlternatives(subject, text_content, settings.SENDER, settings.RECIPIENT)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

