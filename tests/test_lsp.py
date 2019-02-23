import os
import json
import pytest
import platform
from .context import kotlin_kernel as kk
from subprocess import Popen, PIPE, STDOUT


example_file = './Hello.kt'
example_file = os.path.abspath(example_file)

payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'textDocument/hover',
            'params': {
              'textDocument': {
                'uri': f'file://{example_file}'
              },
              'position': {
                'line': 1,
                'character': 9
              }
            }
          }

binary = '../kotlin_kernel/java/bin/kotlin-language-server'
binary = os.path.abspath(binary)

payload_json = json.dumps(payload)
payload_json_utf8 = payload_json.encode('utf-8')
msg = f'Content-Length: {len(payload_json_utf8)}\r\n\r\n'.encode('utf-8') + \
      payload_json_utf8


def send_header(proc, payload_length):
    print(payload_length)
    header = f'Content-Length: {payload_length}\r\nContent-Type: application/vscode-jsonrpc; charset=utf-8\r\n\r\n'.encode('ascii')
    proc.stdin.write(header)


def send_body(proc, payload):
    print(payload.encode('utf-8'))
    proc.stdin.write(payload.encode('utf-8'))


def test_json_rpc():
    p = Popen([binary], stdout=PIPE, stdin=PIPE, stderr=PIPE)

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

    # Now ask for the hover message
    send_header(p, len(payload_json_utf8))
    send_body(p, json.dumps(payload))
    #written_bytes = p.stdin.write(msg)
    #assert written_bytes == len(msg)

    content_length = int(p.stdout.readline()[16:])
    p.stdout.readline()  # read the \r\n
    response = json.loads(p.stdout.read(content_length))
    print(response)

    assert response.decode('utf-8').contains('inline fun')