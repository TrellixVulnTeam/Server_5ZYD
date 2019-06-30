import socket
from Scripts import FileDirectory


def main(client):
    port = 50000  # Reserve a port for your service every new transfer wants a new port or you must wait.
    s = socket.socket()  # Create a socket object
    host = ""  # Get local machine name
    s.bind((host, port))  # Bind to the port
    s.listen(5)  # Now wait for client connection.

    print('Server listening....')
    client.send('CONNECT'.encode("utf-8"))

    connection, address = s.accept()  # Establish connection with client.
    print('Got connection from', address)
    path = FileDirectory.main()
    if path == "":
        print("No file was selected. Closing Send")
        connection.close()
        exit()
    try:
        print(path)
        name = str(path).rsplit("\\", 1)[1]
        name = name.encode("utf-8")
        connection.send(name)
        with open(path, 'rb') as f:
            print('Sending...')
            l = f.read(1024)
            while l:
                connection.send(l)
                l = f.read(1024)
        print('Finished sending')
        connection.close()
    except:
        print("Could not open file please try again")


def get_files(client, path):
    port = 50000  # Reserve a port for your service every new transfer wants a new port or you must wait.
    s = socket.socket()  # Create a socket object
    host = ""  # Get local machine name
    s.bind((host, port))  # Bind to the port
    s.listen(5)  # Now wait for client connection.

    print('Server listening....')
    client.send('CONNECT'.encode("utf-8"))

    conn, addr = s.accept()  # Establish connection with client.
    print('Got connection from', addr)
    try:
        print(path)
        name = str(path).rsplit("\\", 1)[1]
        name = name.encode("utf-8")
        conn.send(name)
        with open(path, 'rb') as f:
            print('Sending...')
            l = f.read(1024)
            while l:
                conn.send(l)
                l = f.read(1024)
        print('Finished Sending sending')
        conn.close()
    except Exception as e:
        print("Could not open file please try again")
        print(e)


if __name__ == '__main__':
    main()
