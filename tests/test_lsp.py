import os
import json
import pytest
import platform
from .context import kotlin_kernel as kk
from subprocess import Popen, PIPE, STDOUT


EXAMPLE_FILE = './Hello.kt'
EXAMPLE_FILE = os.path.abspath(EXAMPLE_FILE)

BINARY = '../kotlin_kernel/java/bin/kotlin-language-server'
BINARY = os.path.abspath(BINARY)


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


def test_hover():
    payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'textDocument/hover',
            'params': {
              'textDocument': {
                'uri': f'file://{EXAMPLE_FILE}'
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
    content_length = int(p.stdout.readline()[16:])
    p.stdout.readline()  # read the \r\n
    response = json.loads(p.stdout.read(content_length))
    print(response)

    # get the second message after start
    content_length = int(p.stdout.readline()[16:])
    p.stdout.readline()  # read the \r\n
    response = json.loads(p.stdout.read(content_length))
    print(response)

    # Now, ask for the hover message
    send_header(p, len(payload_json_utf8))
    send_body(p, json.dumps(payload))
    #written_bytes = p.stdin.write(msg)
    #assert written_bytes == len(msg)

    content_length = int(p.stdout.readline()[16:])
    p.stdout.readline()  # read the \r\n
    response = json.loads(p.stdout.read(content_length))
    print(response)

    assert response.decode('utf-8').contains('inline fun')