import os
import re
import platform
from ipykernel.kernelbase import Kernel
from pexpect.replwrap import REPLWrapper, bash

ANSII_INTERMEDIATE = '\x1b[?1l\x1b>\x1b[?1000l\x1b[?1h\x1b='
ANSII_INTERMEDIATE_SHORT = '\x1b[?1h\x1b='
ANSII_RESULT = '\x1b[?1l\x1b>\x1b[?1000l'

class KotlinKernel(Kernel):
    implementation = 'Kotlin'
    implementation_version = '0.1'
    language = 'kotlin'
    language_version = '0.1'
    language_info = {
        'name': 'kotlin',
        'mimetype': 'text/x-kotlin',
        'file_extension': '.kt',
    }
    banner = "Kotlin kernel - Kotlin in Jupyter Notebooks"

    keywords = ['as', 'as?', 'break', 'class', 'continue', 'do', 'else', 'false', 'for', 'fun', 'if', 'in', 'is', '!in', 'interface', 'is', '!is', 'null', 'object', 'package', 'return', 'super', 'this', 'throw', 'true', 'try', 'typealias', 'val', 'var', 'when', 'while', 'by', 'catch', 'constructor', 'delegate', 'dynamic', 'field', 'file', 'finally', 'get', 'import', 'init', 'param', 'property', 'receiver', 'set', 'setparam', 'where', 'actual', 'abstract', 'annotation', 'companion', 'const', 'crossinline', 'data', 'enum', 'expect', 'external', 'final', 'infix', 'inline', 'inner', 'internal marks a declaration as visible in the current module', 'lateinit', 'noinline', 'open', 'operator', 'out', 'override', 'private', 'protected', 'public', 'reified', 'sealed', 'suspend', 'tailrec', 'vararg', 'field', 'it']

    cmd_timeout = 60

    if platform.system() == 'Windows':
        # TODO: what shall I do on Windows here???
        # my_shell = ...
        pass
    else:
        my_shell = bash(command='bash')


    def start_kotlin_shell(self):
        if platform.system() == 'Windows':
            kotlin_shell_bin = 'kotlinc-jvm.bat'
        else:
            kotlin_shell_bin = 'kotlinc-jvm'
        kotlin = REPLWrapper(kotlin_shell_bin, '>>> ', None,
                             continuation_prompt='... ')
        return kotlin

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self.kotlin_shell = self.start_kotlin_shell()

    def _send_query_to_kotlin_shell(self, code):
        # remove empty lines
        code_lines = [line for line in code.splitlines() if line.strip() != '']
        code = '\n'.join(code_lines)

        result = self.kotlin_shell.run_command(code, timeout=self.cmd_timeout)

        # Filter output. Remove intermediate steps and retain only real outputs
        new_out = []

        for line in result.splitlines()[1:-1]:
            if (line and not line.startswith(ANSII_INTERMEDIATE) and
                not line.startswith(ANSII_INTERMEDIATE_SHORT)):
                if line.startswith(ANSII_RESULT):
                    line = line.replace(ANSII_RESULT, '')
                new_out.append(line)
        # with open('/tmp/output.txt', 'w') as fp:
        #     fp.write('\n'.join(new_out))
        return '\n'.join(new_out)

    def _clean_input(self, code):
        lines = code.splitlines()
        clean_input = '\n'.join([l for l in lines if l])
        return clean_input

    def _is_magic(self, code):
        magic_lines = code.splitlines()
        magic_line = magic_lines[0].strip()
        if magic_line.startswith('%%'):
            return magic_line.replace('%%', ''), '\n'.join(magic_lines[1:])
        else:
            return None, None

    def _send_to_bash(self, code):
        res = self.my_shell.run_command(code, timeout=self.cmd_timeout)
        return res

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        magic, magic_code = self._is_magic(code)
        if magic == 'bash' and magic_code:
            response = self._send_to_bash(magic_code)
            if not silent:
                result = {'data': {'text/plain': response},
                          'execution_count' : self.execution_count}
                self.send_response(self.iopub_socket, 'execute_result',
                                   result)

            exec_result = {'status': 'ok',
                           'execution_count': self.execution_count,
                           'payload': [], 'user_expressions': {}}

            return exec_result
        elif magic:
            # TODO: implement an error for any other magic
            exec_result = {'status': 'error',
                           'execution_count': self.execution_count,
                           'payload': [], 'user_expressions': {}}
            return exec_result

        # then it is a query to Kotlin
        response = self._send_query_to_kotlin_shell(code)

        # No matter what, this is the text response
        result = {'data': {'text/plain': response},
                  'execution_count' : self.execution_count}
        self.send_response(self.iopub_socket, 'execute_result', result)

        exec_result = {'status': 'ok',
                       'execution_count': self.execution_count,
                       'payload': [], 'user_expressions': {}}

        return exec_result

    def do_complete(self, code, cursor_pos):
        space_idxs = [i for i, l in enumerate(code) if l == ' ']
        low_idxs = [s for s in space_idxs if s < cursor_pos]
        if low_idxs:
            low_cp = max([s for s in space_idxs if s < cursor_pos]) + 1
            key_start = code[low_cp:cursor_pos]
        else:
            low_cp = 0
            key_start = code[:cursor_pos]

        matches = [k for k in self.keywords if k.startswith(key_start)]
        content = {'matches' : matches, 'cursor_start' : low_cp,
                   'cursor_end' : cursor_pos, 'metadata' : {}, 'status' : 'ok'}
        return content