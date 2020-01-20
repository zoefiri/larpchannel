
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
                print("escaped!")

            else:
                if escaped == False and char == '(':
                    key_reading = False
                elif escaped == False and char == ')':
                    key_reading = True
                    responses[key_buffer] = val_buffer
                    key_buffer = val_buffer = ""
                elif escaped == False and key_reading == True:
                    key_buffer += char
                elif escaped == False and key_reading == False:
                    val_buffer += char

                escaped = False

    return responses

def find_quote(responses, msg):
    response = ""
    try:
        response = responses[msg]
        break
    except KeyError:
        break
    return response

def add_quote(quote, response):



