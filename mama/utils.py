from BeautifulSoup import BeautifulSoup, Tag
from datetime import datetime

def mobile_number_to_international(mobile_number):
    if mobile_number.startswith('0') and len(mobile_number) == 10:
            mobile_number = '27' + mobile_number[1:]
    return mobile_number


def format_html_string(html_string):
    """Parse a html fragment to plain text"""
    soup = BeautifulSoup(html_string)
    clean_string = ''

    #clean_string = '\n'.join([e.replace("\r", "") for e in soup.recursiveChildGenerator() if isinstance(e, unicode)])
    for e in soup.recursiveChildGenerator():
        if isinstance(e, unicode):
            clean_string += e.replace('\r', '')
        elif isinstance(e, Tag):
            if e.name in ['p', 'br', 'div']:
                clean_string += '\n'
        else:
            pass
    lines = clean_string.split("\n")
    clean_string = "\n\n".join([line.strip() for line in lines if line.strip()])
    return clean_string


def unban_user(user):
    profile = user.profile
    profile.banned = False
    profile.save()

    return profile


def ban_user(user,duration):
    profile = user.profile
    profile.banned = True
    profile.last_banned_date = datetime.now()
    profile.ban_duration = duration
    profile.save()

    return profile