import os
import json
import pytest
import platform
import pathlib
from .context import kotlin_kernel as kk
from subprocess import Popen, PIPE, STDOUT


EXAMPLE_FOLDER = pathlib.Path(os.path.abspath(__file__)).parent
EXAMPLE_FILE = EXAMPLE_FOLDER.joinpath('Hello.kt')

BINARY = '../kotlin_kernel/java/bin/kotlin-language-server'
BINARY = os.path.abspath(BINARY)

LOG_LEVELS = {1: 'Error', 2: 'Warning', 3: 'Info', 4: 'Log'}

current_request_id = 1


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


def send_message(proc, payload):
    """
    Sends a message to the language server.
    """
    payload_json = json.dumps(payload)
    payload_json_utf8 = payload_json.encode('utf-8')
    send_header(proc, len(payload_json_utf8))
    send_body(proc, json.dumps(payload))


def read_message(proc):
    """Reads a message from the language server."""
    content_length = int(proc.stdout.readline()[16:])
    proc.stdout.readline()  # read the \r\n
    response = json.loads(proc.stdout.read(content_length))
    
    return response


def is_method(msg, method):
    """Tests whether a JSON-RPC message references a given method."""
    return ('method' in msg) and (msg['method'] == method)


def is_id(msg, msg_id):
    """Tests whether a JSON-RPC message references a given id."""
    return ('id' in msg) and (msg['id'] == msg_id)


def read_next(proc, method=None, msg_id=None):
    """
    Reads the next message of the specified method (or
    simply the next message if no method is specified) and returns it.
    Handles log messages and errors that occur.
    """
    response = {'method': ''}
    got_message = False
    
    while not got_message:
        response = read_message(proc)
        
        # Print the message while handling special message kinds
        if 'error' in response:
            # Print errors/stack traces to stdout
            error = response['error']
            print(error['message'])
            print(error['data'].replace(r'\r\n', os.linesep))
        elif is_method(response, 'window/logMessage'):
            # Print log message
            log_params = response['params']
            log_level = LOG_LEVELS[log_params['type']]
            log_level = f'[{log_level}]'.ljust(10)
            log_msg = log_params['message']
            print(f'{log_level} {log_msg}')
        else:
            # Print raw JSON
            print(response)
        
        got_message = ((method == None) or is_method(response, method)) and ((msg_id == None) or is_id(response, msg_id))
   
    return response


def ls_call(proc, method, **kwargs):
    """
    Wraps the send_message method into a more convenient function
    for language server calls. Returns the response.
    """
    global current_request_id
    
    req_id = current_request_id
    send_message(proc, {
        'jsonrpc': '2.0',
        'id': req_id,
        'method': method,
        'params': kwargs
    })
    current_request_id += 1
    
    return read_next(proc, msg_id=req_id)
    


def ls_respond(proc, request, **kwargs):
    """
    Wraps the send_message method into a more convenient function
    for responses.
    """
    send_message(proc, {
        'jsonrpc': '2.0',
        'id': request['id'],
        'method': request['method'],
        'params': kwargs
    })


def launch_lang_server():
    """
    Launches the language server and returns
    the started process.
    """
    print(f'Starting language server from {BINARY}')
    p = Popen([BINARY], stdout=PIPE, stdin=PIPE, stderr=PIPE)

    # Send an initialize request to the language server
    ls_call(p, 'initialize',
        processId=None,
        rootUri=EXAMPLE_FOLDER.as_uri(),
        capabilities={}
    )
    
    return p


def test_hover():
    p = launch_lang_server()

    # Now, ask for the hover message
    response = ls_call(p, 'textDocument/hover',
        textDocument={'uri': EXAMPLE_FILE.as_uri()},
        position={'line': 1, 'character': 9}
    )
    
    assert 'inline fun' in response['result']['contents']['value']
