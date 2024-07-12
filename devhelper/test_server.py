#!/usr/bin/env python3
'''
This is a script to set up a local http server for debugging processes.
When active, input an index to change the current FILE being served.
(Remember to keep PORT equal to DEBUG_PORT on bot.py)

'''
import threading
import http.server
import socketserver

FILES = ["null.xml", "first.xml", "second.xml", "third.xml"]
PORT = 8080
path = "null.xml"
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        global path
        self.path = "./devhelper/testcases/" + path
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def serve():
    handler_object = MyHttpRequestHandler
    my_server = socketserver.TCPServer(("", PORT), handler_object)
    my_server.serve_forever()

if __name__ == "__main__":
    print("---ACTIVE---")
    server_thread = threading.Thread(target = serve, args = ())
    server_thread.start()
    while True:
        new_index = int(input())
        if new_index < 0 or new_index >= len(FILES):
            continue
        path = FILES[new_index] # could cause a data race but for now is fine
        print(f"UPDATE -> {path}")
        index = new_index