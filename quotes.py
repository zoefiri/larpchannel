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
                elif key_reading == True:
                    key_buffer += char
                elif key_reading == False:
                    val_buffer += char

                escaped = False

    file.close()
    return responses

def find_quote(responses, msg):
    response = ""
    try:
        response = responses[msg.lower()]
    except KeyError:
        pass
    print(responses)
    return response

def add_quote(quote, response):
    quote = quote.replace("(", "\(")
    quote = quote.replace(")", "\)")
    response = response.replace("(", "\(")
    response = response.replace(")", "\)")

    file = open("responses.txt", "rb+")
    file.seek(-1,2)
    if file.read(1) == '\n':
        file.seek(-1,2)
    else:
        file.seek(0,2)
    file.write(str.encode(quote.lower() + '(' + response + ')'))
    file.close()
