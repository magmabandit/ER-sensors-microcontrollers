Will make this more markdown friendly in the future....


Steps to get this loaded on the Pi... 

```shell
sudo apt install hiredis libcjson-dev redis-server
gcc -o canReader canReader.c -lhiredis -lcjson
```

I think redis pub/sub might be a good way for the different applications to communicate. So this reader application
will publish messages with the information the aggregator need. The aggregator should subscribe to these messages and
do what it needs to with the data.

For this to work, we need a redis server running. There are several options for doing this but I'll document these 2.

1. Single terminal/window (preferred)
We can use a library like `tmux` to allow redis to be run behind the scenes and allow te publisher to be run all in a 
single terminal window. Here's a [cheat sheet](https://tmuxcheatsheet.com/) for tmux.
2. Multiple windows
Connect to the pi with separate terminals. In the first, start the redis server. In the other, compile and run the reader. This approach
is less preferred because it requires an active session. tmux will continue to run even when the session is ended. 