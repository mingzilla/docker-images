## How to Verify

I want to test if you can do this, because this is using ollama with gemma4:e4b model in claude code, please test, then tick or cross these boxes, if you can use multiple sub-agents to do this that would be even better

| Capability      | Test prompt                                                                   | Works? |
|-----------------|-------------------------------------------------------------------------------|--------|
| File read       | read /etc/hostname                                                            |        |
| File glob       | list all .sh files in this directory                                          |        |
| File grep       | search for OLLAMA_HOST in this directory                                      |        |
| File write      | create /tmp/test.txt with "hello"                                             |        |
| File edit       | replace "hello" with "world" in /tmp/test.txt                                 |        |
| Shell command   | run uname -a                                                                  |        |
| Web search      | search the web for "ollama gemma4:e4b"                                    |        |
| Web fetch       | fetch https://example.com and summarize it                                    |        |
| Parallel agents | search for "TODO" and "FIXME" in this directory in parallel                   |        |
| MCP server      | list available MCP tools                                                      |        |
| Python coding   | write a python script that prints fibonacci numbers to /tmp/fib.py and run it |        |
| Shell scripting | write a bash script that prints disk usage to /tmp/disk.sh and run it         |        |

---

## Results: gemma4:e4b — YYYY-MM-DD

| Capability      | Test prompt                                                                   | Works? | Notes |
|-----------------|-------------------------------------------------------------------------------|--------|-------|
| File read       | read /etc/hostname                                                            |        |       |
| File glob       | list all .sh files in this directory                                          |        |       |
| File grep       | search for OLLAMA_HOST in this directory                                      |        |       |
| File write      | create /tmp/test.txt with "hello"                                             |        |       |
| File edit       | replace "hello" with "world" in /tmp/test.txt                                 |        |       |
| Shell command   | run uname -a                                                                  |        |       |
| Web search      | search the web for "ollama gemma4:e4b"                                    |        |       |
| Web fetch       | fetch https://example.com and summarize it                                    |        |       |
| Parallel agents | search for "TODO" and "FIXME" in this directory in parallel                   |        |       |
| MCP server      | list available MCP tools                                                      |        |       |
| Python coding   | write a python script that prints fibonacci numbers to /tmp/fib.py and run it |        |       |
| Shell scripting | write a bash script that prints disk usage to /tmp/disk.sh and run it         |        |       |
