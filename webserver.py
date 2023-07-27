#Importing various modules to use the fuctions 
import threading
import socket
import signal
import os
import sys
import argparse
import time

host = "localhost"
PORT = 8008 #default Value for the port number
SERVER_DIRECTORY = './' #default Value for the directory

def HttpsThreadConn(request, connection):
    print(request)
    print(connection)
    if(request[1] == '/'):
        request[1] = '/index.html'
    try:
        if(request[1].find('.html') > 0):
            filenames = SERVER_DIRECTORY + request[1]
            #opening the files
            with open(filenames,  'r', encoding='latin-1') as f:
                content = f.read()
            #read all the data in to content variable 
            f.close()
            #using close() to close the file
            res = str.encode("HTTP/1.1 200 ok\n")
            res = res + str.encode('Content: text/html\n')
            res = res + str.encode('\r\n')
            print(res)
            connection.sendall(res)
            connection.sendall(content.encode())
        elif(request[1].find('.png') > 0 or request[1].find('.jpeg') > 0 or  request[1].find('.jpg') > 0 or  request[1].find('.txt') > 0 or request[1].find('.gif') > 0):
            image_type = request[1].split('.')[1]
            filenames = '.' + request[1]
            image_data = open(filenames, 'rb')
            res = str.encode("HTTP/1.1 200 OK\n")
            image_type = "Content-Type: image/" + image_type +"\r\n"
            res = res + str.encode(image_type)
            res = res + str.encode("Accept-Ranges: bytes\r\n\r\n")
            connection.sendall(res)
            connection.sendall(image_data.read())
        elif(request[1].find('*') > 0):
            connection.sendall(str.encode("HTTP/1.1 403 Forbidden\r\nForbidden"))
        elif(request[1].find('badrequest.jpg') > 0):   
            connection.sendall(str.encode("HTTP/1.1 400 Bad Request\r\nBad Request"))
        else:
            connection.sendall(str.encode("HTTP/1.1 404 NOT FOUND\r\nFile Not Found"))
    except FileNotFoundError:
        connection.sendall(str.encode("HTTP/1.1 404 NOT FOUND\r\nFile Not Found"))
    except Exception:
        connection.sendall(str.encode("HTTP/1.1 500 Internal Server Error\r\nInternal Server Error"))


#The funtion is used for the socket Listener used for the multi threading
def socketListener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketV:
        socketV.bind((host, PORT))
        while True:
            socketV.listen()
            conn, address = socketV.accept()
            threadAlive = threading.Thread(target=keepAliveConnection, args=(conn, address))
            threadAlive.start()

#This function is used for keeping the connection alive
def keepAliveConnection(connection, address):
    size = 1024
    with connection:
        #setting the connetion to be alive for 5 Seconds
        connection.settimeout(5)
        while True:
            try:
                request = connection.recv(size).decode()
                headers = request.split('\r\n')
                REQUEST  = headers[0].split()
                if REQUEST[0] == "GET":
                    HttpsThreadConn(REQUEST,connection)
            except Exception as e:
                break
    #close the connection
    connection.close()


#This is the main funrion where the aruguments from the user input are used here
if __name__ == "__main__":
    #using the argument parser to get the user inputs like documnet folder and port
    inputData = argparse.ArgumentParser()
    inputData.add_argument('-document_root', type=str)
    inputData.add_argument('-port', type=int)
    argumentValues = inputData.parse_args()
    try:
        PORT = argumentValues.port
        SERVER_DIRECTORY = argumentValues.document_root
    except AttributeError:
        #Executed when there is some attribute arrors
        print("Attribute error due to invalid arguments")
        print("Usage: python .\webserver.py -document_root './' -port 8008")
        Print("Port in Use")
        sys.exit(1)
    print("The Server is launched" + host + ":" + str(PORT))
    print("The Directory is" + SERVER_DIRECTORY)
    socketListener()
