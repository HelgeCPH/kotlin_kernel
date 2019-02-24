import os
import json
import pytest
import platform
import pathlib
from .context import kotlin_kernel as kk
from subprocess import Popen, PIPE, STDOUT


EXAMPLE_FILE = os.path.join(__file__, '..', 'Hello.kt')
EXAMPLE_FILE = pathlib.Path(os.path.abspath(EXAMPLE_FILE)).as_uri()

BINARY = '../kotlin_kernel/java/bin/kotlin-language-server'
BINARY = os.path.abspath(BINARY)


def set_binary(path):
    """
    Sets the path to the language server binary. This function
    can be used to conveniently swap the binary at runtime or
    in an interactive shell.
    """
    global BINARY
    BINARY = os.path.abspath(path)


def send_header(proc, payload_length):
    """
    Send the header of the JSON RPC via stdin to the process `proc`

    According to the specification, see
    https://microsoft.github.io/language-server-protocol/specification, the
    header fields have to be encoded as ASCII.

    I do not know if the `Content-Type` field is optional, anyways currently I
    do not get a response from the server either way.
    """
    print(payload_length)
    header = f'Content-Length: {payload_length}\r\nContent-Type: application/vscode-jsonrpc; charset=utf-8\r\n\r\n'.encode('ascii')
    proc.stdin.write(header)


def send_body(proc, payload):
    """
    After sending the header this message can be send to the language server.

    According to the specification, see
    https://microsoft.github.io/language-server-protocol/specification, the
    actual JSON RPC message has to be encoded as UTF-8.
    """
    print(payload.encode('utf-8'))
    proc.stdin.write(payload.encode('utf-8'))
    proc.stdin.flush()


def read_message(proc):
    """
    Reads a message from the language server.
    """
    content_length = int(proc.stdout.readline()[16:])
    proc.stdout.readline()  # read the \r\n
    response = json.loads(proc.stdout.read(content_length))
    if 'error' in response:
      error = response['error']
      print(error['message'])
      print(error['data'].replace(r'\r\n', os.linesep))
    return response


def is_method(msg, method):
    """
    Tests whether a JSON-RPC message references a given method.
    """
    return ('method' in msg) and (msg['method'] == method)


def test_hover():
    payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'textDocument/hover',
            'params': {
              'textDocument': {
                'uri': EXAMPLE_FILE
              },
              'position': {
                'line': 1,
                'character': 9
              }
            }
          }

    payload_json = json.dumps(payload)
    payload_json_utf8 = payload_json.encode('utf-8')

    p = Popen([BINARY], stdout=PIPE, stdin=PIPE, stderr=PIPE)

    # get the first message after start
    print(read_message(p))

    # get the second message after start
    print(read_message(p))

    # Now, ask for the hover message
    send_header(p, len(payload_json_utf8))
    send_body(p, json.dumps(payload))
    #written_bytes = p.stdin.write(msg)
    #assert written_bytes == len(msg)

    response = {'method': ''}
    while not is_method(response, 'textDocument/hover'):
      response = read_message(p)
      print(response)
    
    assert response.decode('utf-8').contains('inline fun')
