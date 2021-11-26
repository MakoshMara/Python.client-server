
import json

def get_message(client):

    from lesson3.common.variables import MAX_PACAGE_LEGTH
    from lesson3.common.variables import ENCODING

    encoded_responce = client.recv(MAX_PACAGE_LEGTH)
    if isinstance(encoded_responce,bytes):
        json_responce = encoded_responce.decode(ENCODING)
        response = json.loads(json_responce)
        if isinstance(response,dict):
            return response
        raise ValueError
    raise ValueError

def send_meccage(sock, message):
    from lesson3.common.variables import ENCODING
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)

