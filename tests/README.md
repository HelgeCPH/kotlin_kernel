# How to run the tests?

Run the tests with `pytest -s` to see intermediate `print` messages.


-------

I send the following question as issue to https://github.com/fwcd/KotlinLanguageServer/issues/89


# KotlinLanguageServer not responding to stdout?


I am new to the language server protocol and it might be that my question is stupid, however I would appreciate any help. Since I do not know where else to ask it, I am asking here. In case it is not the right place please point me to to a more suitable forum.

Currently, I am working on a [Kotlin kernel for Jupyter](https://github.com/HelgeCPH/kotlin_kernel/tree/lsp_test) for which I would like to use this Kotlin language server for code completion.

If I understand it right, the language server responds (via stdout) to JSON-RPC calls, which are send via stdin.

However, I cannot get a corresponding response from the server when sending a JSON RPC message. To better explain what I tried to do, I built [a small test](https://github.com/HelgeCPH/kotlin_kernel/blob/lsp_test/tests/test_lsp.py), which sends a JSON RPC request corresponding to hovering over a bit of code. However, it seems as if the Kotlin LSP does not return anything. The test keeps on hanging. It keeps on waiting to read from stdout of the Kotlin LSP after sending the following message:

```
b'Content-Length: 215\r\n\r\n{"jsonrpc": "2.0", "id": 1, "method": "textDocument/hover", "params": {"textDocument": {"uri": "file:///Users/bumm/Documents/documents/python/kotlin_kernel/tests/Hello.kt"}, "position": {"line": 2, "character": 9}}}'
```

But it seems as if there is nothing coming back.

I would expect some kind of response in JSON format (after corresponding headers) containing one or more strings with `inline fun println(message: Any?): Unit`, which would correspond to [the text that is displayed when hovering over line two column nine in](https://github.com/HelgeCPH/kotlin_kernel/blob/lsp_test/tests/Hello.kt), see:

![](https://github.com/HelgeCPH/kotlin_kernel/blob/lsp_test/tests/hover.png?raw=true)


My questions:

  * Is there a way to see the requests and responses between the VSCode plugin and the Kotlin language server?
    - I tried to inspect your test-suite but all communication between the client and the server is wrapped in code and I cannot find where that code is translated to JSON RPC format.
    - I see your [comment on debugging in BUILDING.md](https://github.com/fwcd/KotlinLanguageServer/blob/master/BUILDING.md#debugging). Is this where I could see the messages directly? If so, what do I have to do precisely? Unfortunately, I do not really understand the comment.
  * Do I have to send other JSON RPC requests to the server before sending the one to hover?
    - If so, why does the server not return an error message? Currently, it is just silent.




Everything that I know about the LSP so far comes from it's specification document: https://microsoft.github.io/language-server-protocol/specification
Consequently, I would really appreciate any help.

