def mobile_number_to_international(mobile_number):
    if mobile_number.startswith('0') and len(mobile_number) == 10:
            mobile_number = '27' + mobile_number[1:]
    return mobile_number

