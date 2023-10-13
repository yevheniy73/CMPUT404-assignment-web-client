#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2023 Yevhen Kaznovskyi
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

#---------------------------------------------------------------------
HTTP1_1 = 'HTTP/1.1\r\n'
HOST = 'Host:'
ACCEPT_CHARS = 'Accept-Charset: UTF-8\r\n'
URL_ENCODED = 'Content-Type: application/x-www-form-urlencoded\r\n'
CONTENT_LENGTH = 'Content-Length:'
CON_CLOSE = 'Connection:close\r\n\r\n'
#---------------------------------------------------------------------

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
#------------------------------------------------------------------------------------------------------------------------------------------------
    def get_host_port(self, url_parse):
        port_number = url_parse.port
        port_number = port_number if port_number else 80

        return port_number
    
#------------------------------------------------------------------------------------------------------------------------------------------------   
    def get_path_component(self, url_parse):
        path_component = url_parse.path
        path_component = path_component if path_component else "/"

        return path_component
    
#------------------------------------------------------------------------------------------------------------------------------------------------
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        status_line = data.split('\r\n')[0]
        status_code = status_line.split()[1]
        return int(status_code)

    def get_headers(self,data):
        response_headers = data.split('\r\n\r\n')[0]
        return str(response_headers)

    def get_body(self, data):
        response_body = data.split('\r\n\r\n')[1]
        return str(response_body)
    
#------------------------------------------------------------------------------------------------------------------------------------------------
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
#------------------------------------------------------------------------------------------------------------------------------------------------
    def GET(self, url, args=None):

        url_parse = urllib.parse.urlparse(url)
        port_number = self.get_host_port(url_parse)
        path_component = self.get_path_component(url_parse)
        domain_name = url_parse.hostname
    
        self.connect(domain_name, port_number)

        request = f"GET {path_component} {HTTP1_1}{HOST} {domain_name}\r\n{ACCEPT_CHARS}{CON_CLOSE}"
        self.sendall(request)

        http_response = self.recvall(self.socket)
        
        code = self.get_code(http_response)
        body = self.get_body(http_response)
        self.close()
        
        return HTTPResponse(code, body)
    
#------------------------------------------------------------------------------------------------------------------------------------------------
    def POST(self, url, args=None):

        url_parse = urllib.parse.urlparse(url)
        port_number = self.get_host_port(url_parse)
        path_component = self.get_path_component(url_parse)
        domain_name = url_parse.hostname

        self.connect(domain_name, port_number)

        args_urlencoded = urllib.parse.urlencode(args) if args else ''
        args_urlencoded_length = str(len(args_urlencoded))

        request = f"POST {path_component} {HTTP1_1}{HOST} {domain_name}\r\n{URL_ENCODED}{CONTENT_LENGTH} {args_urlencoded_length}\r\n{CON_CLOSE}{args_urlencoded}"
        self.sendall(request)

        http_response = self.recvall(self.socket)

        code = self.get_code(http_response)
        body = self.get_body(http_response)
        self.close()

        return HTTPResponse(code, body)
    
#------------------------------------------------------------------------------------------------------------------------------------------------

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
