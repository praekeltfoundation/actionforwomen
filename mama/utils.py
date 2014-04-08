from BeautifulSoup import BeautifulSoup


def mobile_number_to_international(mobile_number):
    if mobile_number.startswith('0') and len(mobile_number) == 10:
            mobile_number = '27' + mobile_number[1:]
    return mobile_number


def format_html_string(html_string):
    #PARSE HTML INTO PLAIN TEXT
    soup = BeautifulSoup(html_string)

    clean_string = '\n'.join([e.replace("\r", "") for e in soup.recursiveChildGenerator() if isinstance(e, unicode)])
    return clean_string
