import json

def retrieve_quotes():
    file = open("responses.txt", "r")
    escaped = False
    responses = {}
    key_reading = True
    key_buffer = ""
    val_buffer = ""

    while True:
        line = file.readline()
        if not line: break

        for char in line:
            if char == '\\' and escaped == False:
                escaped = True
            elif char == '\\':
                if key_reading:
                    key_buffer += char
                else:
                    val_buffer += char

            else:
                if not escaped and char == ':' and key_reading:
                    key_reading = False
                elif not escaped and char == ':' and not key_reading:
                    key_reading = True
                    responses[key_buffer] = val_buffer
                    key_buffer = val_buffer = ""
                elif key_reading:
                    key_buffer += char
                elif not key_reading:
                    val_buffer += char

                escaped = False

    file.close()
    return responses

def find_quote(responses, msg):
    response = ""
    try:
        print('attempt')
        response = responses[msg.lower()]
    except KeyError:
        pass
    return response

def del_quote(responses, quote):
    try:
        del responses[quote]
    except KeyError:
        return 1

    file = open("responses.txt", "w")
    for quote_l in responses:
        file.write(quote_l.replace(":", "\\:"))
        file.write(':')
        file.write(responses[quote_l].replace(":", "\\:"))
        file.write(':')

    file.close()
    return 0
