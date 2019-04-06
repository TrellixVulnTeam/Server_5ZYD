from Scripts import BackupEngine
from Scripts import Compare_Engine
from Scripts import FileDirectory
from Scripts import Get
from Scripts import File_Sender
import os
import socket
import sys
import time
import types
import uuid
import subprocess
import selectors
from threading import Thread
import pyautogui
from pyautogui import press

FNULL = open(os.devnull, 'w')

global do_not_read
global found
global rcn
global rm_first
global rm_message
global rm_sock
global accepted
global recv_computer_name
global waiting_on_server
global done
global test_computername
global connected
global started

global replacing_dict
global dict
global IP
global a
global b
global conn
global sock1
global sock2
global got
global sock
global in_messaging
global back_message
global back
global message
global go_back
global MAC

connected = False
got = False
dict = {}
replacing_dict = False
show_ls = True
results = []
rm = False

sel = selectors.DefaultSelector()
pyautogui.FAILSAFE = False


def error_log(error):
    with open("Resources\\ErrorLog.txt", 'a') as file:
        file.write(time.ctime() + "\n")
        file.write(str(error) + "\n" + "\n")


def error_print(error_message ,error):
    print("SYSTEM ERROR - " + error_message + ": " + str(error))


def write_backup_files(pc, sock1):
    s = get_ip_from_sock(sock1)
    print(s)
    Get.write_backup_file(pc, s)


def rm_send():
    pass


def wake_func(message):
    global found
    WOL_first = "$Mac = "
    WOL_second = '''\n$MacByteArray = $Mac -split "[:-]" | ForEach-Object { [Byte] "0x$_"}
[Byte[]] $MagicPacket = (,0xFF * 6) + ($MacByteArray  * 16)
$UdpClient = New-Object System.Net.Sockets.UdpClient
$UdpClient.Connect(([System.Net.IPAddress]::Broadcast),7)
$UdpClient.Send($MagicPacket,$MagicPacket.Length)
$UdpClient.Close()'''
    with open("Resources/Profiles.txt", "r") as f:
        results = f.read().split(',')
        length = len(results)
        length = length - 1
        i = 0
        j = 0
        print("Computer profile list: ")
        while i != length:
            Name = results[i]
            i += 1
            PC_Name = results[i]
            i += 2
            print('\t' + Name + " - " + PC_Name)
        i = 0
        found = False
        while i != length:
            Name = results[i]
            i += 2
            MAC = results[i]
            i += 1
            if message == Name:
                print('Waking up -> ' + Name + " -> MAC -> " + MAC)
                write2 = WOL_first + '"' + MAC + '"' + WOL_second
                f = open("Resources\\MAC.ps1", "w+")
                f.write(write2)
                f.close()
                subprocess.call(["Resources\\MAC.bat"], stdout=sys.stdout)
                i = length
                found = True

        if found is not True:
            print("COULD NOT FIND " + message)
        press('enter')
        return found


def view_func():
    global dict
    Q = input("Would you like to send or get?")
    if Q == "get":
        Q = input('On which computer would you like to view:\n')
        ls_func()
        print('Server')
    elif Q == "send":
        Q = input('On which computer would you like to view:\n')
        ls_func()
        print('Server')
    else:
        print('exiting program please try again with a proper input')
        return

    file = FileDirectory.main()


def get_ip_addresses_func():
    address_list = socket.getaddrinfo(socket.gethostname(), None)

    ip_list = []
    for item in address_list:
        ip_list.append(item[4][0])

    num = len(ip_list)
    i = 0
    print("SYSTEM: Connect to server with these addresses:")
    print("\t" + socket.gethostname())
    while i != num:
        if str(ip_list[i]).__contains__("::"):
            ip_list.remove(ip_list[i])
            num = num - 1
        print("\t" + ip_list[i])
        i += 1
    return ip_list


def get_ip_from_sock(sock):
    sock = str(sock).rsplit("raddr=('", 1)[1]
    sock = str(sock).rsplit("',", 1)[0]
    return sock


def backup_func(Q):
    length = len(dict)
    if length == 1:
        try:
            for x in dict.values():
                message = "||BACKUP||"
                message = message.encode("utf-8")
                sock1 = x
                time.sleep(0.5)
                sock1.send(message)
                print('finished sending')
        except:
            pass
    else:
        try:
            Q = Q.split('/backup ', 1)[1]
            if Q in str(dict):
                message = "||BACKUP||"
                message = message.encode("utf-8")
                sock1 = dict[Q]
                sock1.send(message)
            else:
                print("Unable to find the computer. Please try again")
        except:
            print("Here is the list of computers:")
            ls_func()
    s = get_ip_from_sock(sock1)
    print(s)
    name = Get.backup(s)
    BackupEngine.main(name)
    getter, path = Compare_Engine.main(name)
    if getter:
        message = "--GETFILES--"
        message = message.encode("utf-8")
        sock1.sendall(message)
        File_Sender.get_files(path)
    else:
        pass


def server_restart():
    print('SYSTEM: Restarting server...')
    time.sleep(1)
    os._exit(1)


def enter_func():
    press('enter')


def pc_and_ip():
    global dict
    i = 1
    for x in dict:
        raddr = str(dict).split("raddr=")[i]
        raddr = raddr.split(">")[0]
        print("\t" + x + " -> IP  -> " + raddr)
        i += 1


def back_func():
    global back_message
    global back
    global in_messaging
    print("Returning to main screen. Please hold")
    time.sleep(1)
    press('enter')
    time.sleep(1)
    back_message = "/back"
    back = True
    press('enter')
    in_messaging = False
    go_back = False


def message_func(Q):
    global rm_message
    global rm
    global rm_sock
    global in_messaging
    global back_message
    global back
    back = False
    back_message = ""
    length = len(dict)
    if length == 1:
        try:
            only_client = 'sending message to only connected client'
            if rm is True:
                print(only_client)
                rm_sock.sendall(only_client.encode("utf-8"))
            else:
                print(only_client)
            for x in dict.values():
                if rm is True:
                    message = rm_message
                else:
                    while back_message != "/back":
                        if back is False:
                            in_messaging = True
                            message = input(" -> ")
                            back_message = message
                            message = message.encode("utf-8")
                            sock1 = x
                            sock1.send(message)
                        else:
                            back_message = "/back"
                    in_messaging = False
        except Exception as error:
            error_log(error)
    else:
        try:
            Q = Q.split('/m ', 1)[1]
            if Q in str(dict):
                back_message = ""
                while back_message != "/back":
                    if back == False:
                        in_messaging = True
                        message = input("Sending message to -> " + Q + " -> ")
                        back_message = message
                        message = message.encode("utf-8")
                        sock1 = dict[Q]
                        sock1.send(message)
                    else:
                        back_message = "/back"
                in_messaging = False
            else:
                if rm is True:
                    print("Computer not found. Please reference the computer list:")
                    rm_sock.sendall("Computer not found. Please reference the computer list:")
                    ls_func()

        except Exception as e:
            print(e)
            print("Here is the list of computers:")
            ls_func()


def help_func():
    print("/m - 'DEVICE NAME' --> Sends message to device, \n"
          "/m - all --> Sends message to all devices, \n"
          "/power 'DEVICE NAME' --> Turns on device, \n"
          "/shutdown 'DEVICE NAME' --> Shutsdown device, \n"
          "/ls --> Shows connected devices, \n"
          "/back --> Exists messaging menu, \n")


def ls_func():
    global dict
    print("Computers currently connected:")
    for x in dict:
        print("\t" + x)


def send_to_func(user_input, sending_socket):
    global IP
    global in_messaging
    global soc
    global rm
    global rm_sock
    length = len(dict)
    if length == 1:
        try:
            message = 'SYSTEM: CANNOT PERFORM ACTION DUE TO THERE ONLY BEING ONE CLIENT'
            print(message)
            for x in dict.values():
                sock1 = x
                sock1.send(message.encode("utf-8"))
        except:
            pass
    else:
        try:
            pc_name = user_input.split('/send ', 1)[1]
            print(pc_name)
            if pc_name in str(dict):
                requesting_message = "--SENDING_FILE_TO--" + str(sending_socket)
                requesting_message = requesting_message.encode("utf-8")
                requesting_socket = dict[pc_name]
                requesting_socket.send(requesting_message)
                sending_message = "--CLIENT_ID--" + str(requesting_socket)
                sending_socket.send(sending_message.encode("utf-8"))
                print("Done sending")
            else:
                print("Computer not found. Please reference the computer list:")
                ls_func()
        except Exception as error:
            error_log(error)
            print("Here is the list of computers:")
            ls_func()


def send_func(Q):
    global IP
    global in_messaging
    global soc
    global rm
    global rm_sock
    length = len(dict)
    if length == 1:
        try:
            message = 'sending file to only connected client'
            if rm is True:
                print(message)
                rm_sock.sendall(message.encode("utf-8"))
            else:
                print(message)
            for x in dict.values():
                message = "--SENDING_FILE--"
                message = message.encode("utf-8")
                sock1 = x
                sock1.send(message)
                print(" Please select file...")
                File_Sender.main()
        except:
            pass
    else:
        try:
            if Q.__contains__('/send '):
                Q = Q.split('/send ', 1)[1]
            print(Q)
            if Q in str(dict):
                message = "--SENDING_FILE--"
                message = message.encode("utf-8")
                sock1 = dict[Q]
                sock1.send(message)
                print(" Please select file to send to -> " + Q)
                File_Sender.main()
            else:
                print("Computer not found. Please reference the computer list:")
                ls_func()
        except:
            print("Here is the list of computers:")
            ls_func()


def rm_func(sock):
    global rm_sock
    global rm
    rm_sock = sock
    rm = True
    message = ""
    length = len(dict)
    '''
    while message != "/back":
        message = input(" -> ")
        if message.__contains__("/send"):
            send_func(message, rm)
        if message.__contains__("/get"):
            pass
        if message.__contains__("/view"):
            pass
    return
'''


def accept_wrapper(sock):
    global do_not_read
    global conn
    global accepted
    conn, addr = sock.accept()  # Should be ready to read
    print('Accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    accepted = True


def service_connection(key, mask):
    global sock
    global sock
    global recv_computer_name
    global selectors
    global sock1
    global dictList
    global Position
    global replacing_dict
    global IP
    global connected
    global in_messaging
    global new_client
    global back
    global show_ls
    global dict
    global waiting_on_server
    global got
    global done
    global accepted
    global MAC
    sock = key.fileobj
    done = True
    if sock not in dict.values():
        if accepted is True:
            if replacing_dict is False:
                new_client = True
                random = str(uuid.uuid4())
                random = random[:4]
                random = 'temporary' + str(random)
                dict[str(random)] = sock
                with open('Resources/Profiles.txt', 'r') as f:
                    print("Please wait for system to configure new computer...")
                    try:
                        got = False
                        waiting_on_server = True
                        print('Waiting to receive computer name')
                        try:
                            c.start()
                        except Exception as error:
                            error_log(error)
                            pass
                        while done is True:
                            time.sleep(.1)
                        client_host_name = recv_computer_name
                        print("Received computer name -> " + client_host_name)
                        waiting_on_server = False
                        got = True
                    except:
                        client_host_name = "failed"
                    profile_txt = f.read().split(',')
                    length = len(profile_txt)
                    length = length - 1
                    i = 0
                    detected = False
                    print("Computer profile list: ")
                    while i != length:
                        profile_common_name = profile_txt[i]
                        i += 1
                        profile_host_name = profile_txt[i]
                        i += 2
                        print('\t' + profile_common_name + " - " + profile_host_name)
                    i = 0
                    while i != length:
                        profile_common_name = profile_txt[i]
                        i += 1
                        profile_host_name = profile_txt[i]
                        i += 2
                        try:
                            if client_host_name == profile_host_name:
                                print('Detected -> ' + profile_common_name + " -> Hostname -> " + profile_host_name)
                                detected = True
                                del dict[random]
                                if profile_common_name in dict:
                                    print("Computer with same hostname found. Creating temporary name for client...")
                                    random = str(uuid.uuid4())
                                    random = random[:4]
                                    profile_common_name = profile_common_name + str(random)
                                dict[profile_common_name] = sock
                                print('Computers currently connected:')
                                pc_and_ip()
                                new_client = False
                                if in_messaging is True:
                                    back_func()
                                else:
                                    enter_func()
                                i = length
                                enter_func()
                        except Exception as error:
                            print("SYSTEM ERROR: " + str(error))
                        try:
                            if client_host_name == "failed":
                                print('could not get hostname. Assigning random value for computer')
                                detected = True
                                print(dict)
                                try:
                                    del dict[random]
                                    random = str(uuid.uuid4())
                                    random = random[:4]
                                    name = "COMPUTER" + str(random)
                                    show_ls = True
                                    if show_ls is True:
                                        dict[name] = sock
                                        show_ls = False
                                        ls_func()
                                    print(dict)
                                    new_client = False
                                    if in_messaging is True:
                                        back_func()
                                    else:
                                        enter_func()
                                    i = length
                                    server_restart()
                                except Exception as error:
                                    print("SYSTEM ERROR: " + str(error))
                        except Exception as error:
                            print("SYSTEM ERROR" + str(error))

                    if detected is False:
                        try:
                            print('New computer detected. Please wait for system to configure')
                            enter_func()
                            time.sleep(1)
                            one = input("What is the name of this computer: ")
                            del dict[random]
                            dict[one] = sock
                            print(dict)
                            new_client = False
                            print("Adding " + one + " to computer profiles")
                            comma = ","
                            with open("Resources\\Profiles.txt", 'a', newline='') as resultFile:
                                resultFile.write(one + comma + client_host_name + comma + MAC + comma)
                            if in_messaging is True:
                                back_func()
                            else:
                                enter_func()
                        except Exception as error:
                            print("SYSTEM ERROR - adding PC to Profiles.txt: " + str(error))
                            error_log(error)
                            print("Error adding new computer. Check delete (005)")
        if connected is False:
            connected = True
        done = True
        accepted = False
        got = False


class Starter(Thread):
    global soc

    def __init__(self):
        global soc

        Thread.__init__(self)
        print("SYSTEM: Starting server")

        host = ''
        port = 8888

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            server_sock.bind((host, port))
        except Exception as e:
            print("Bind failed. Error : " + str(e))
            sys.exit()

        server_sock.listen(5)
        print("SYSTEM: Socket created")
        server_sock.setblocking(False)
        sel.register(server_sock, selectors.EVENT_READ, data=None)

    def run(self):
        while True:
            try:
                events = sel.select()
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        service_connection(key, mask)
            except Exception as error:
                error_log(error)
                error_print("Starter thread, tried registering with no computers connected", error)
                server_restart()


class Send(Thread):
    global in_messaging

    def __init__(self):
        Thread.__init__(self)
        global in_messaging
        print("SYSTEM: Send initialized")

    def run(self):
        print("SYSTEM: Send started")
        global in_messaging
        while True:
            in_messaging = False
            user_input = input(' -> ')
            if user_input == "":
                pass
            if user_input == "/restart":
                server_restart()
            if user_input == "/ls":
                ls_func()
            if user_input.__contains__('/send'):
                send_func(user_input)
            if user_input == "/help":
                help_func()
            if user_input.__contains__('/m'):
                message_func(user_input)
            if user_input == "/backup":
                backup_func(user_input)
            if user_input == 'test':
                i = len(dict)
                i = 0
                while i < len(dict):
                    check = list(dict.values())[i]


class Receive(Thread):
    global sock
    global MAC
    global back
    global message
    global go_back
    global got
    global recv_computer_name
    global waiting_on_server
    global dict
    global done

    def __init__(self):

        global MAC
        global waiting_on_server
        global back
        global message
        global sock
        global dict
        global got
        global recv_computer_name
        global done
        Thread.__init__(self)
        print("SYSTEM: Receive initialized")

    def run(self):
        global MAC
        print('SYSTEM: Receive started')
        global recv_computer_name
        global back
        global message
        global sock
        global got
        global go_back
        global dict
        global waiting_on_server
        global done
        success = False
        while True:
            if got is False:
                try:
                    my_dict = dict
                    for x in my_dict.values():
                        if success is False:
                            try:
                                sock = x
                                recv_data = sock.recv(1024).decode()
                                success = True
                                used_sock = sock
                                if str(recv_data).__contains__("--PCNAME--||"):
                                    if done is True:
                                        useless, recv_computer_name, MAC = str(recv_data).split("||")
                                        done = False
                                else:
                                    if str(recv_data) == "--SENDING_FILE--":
                                        print('Receiving file...')
                                        i = GetThread(x)
                                        i.start()
                                        # recv_data = sock.recv(1024).decode()
                                    elif str(recv_data).__contains__("--GET--"):
                                        print('get initiated')
                                    elif str(recv_data).__contains__("--SEND_TO--"):
                                        message = recv_data.split("--SEND_TO--")[1]
                                        print('sending file to ' + message)
                                        i = SendToThread(message, x)
                                        i.start()
                                    elif str(recv_data).__contains__("--WAKE--"):
                                        message = recv_data.split("--WAKE--")[1]
                                        print('Waking up -> ' + message)
                                        found = wake_func(message)
                                        if found is False:
                                            message = 'COULD NOT FIND ' + message
                                            sock.sendall(message.encode("utf-8"))
                                        else:
                                            message = 'FINISHED WAKING ' + message
                                            sock.sendall(message.encode("utf-8"))
                                    elif str(recv_data).__contains__("--SENDING_BACKUP_FILES--"):
                                        print("GOT BACKUP FILE")
                                        message = recv_data.split("--SENDING_BACKUP_FILES--")[1]
                                        i = OtherBackupThread(message, sock)
                                        i.start()
                                    elif str(recv_data).__contains__("--BACKUP--"):
                                        print("BACKING UP")
                                        message = recv_data.split("--BACKUP--")[1]
                                        i = BackupThread(message)
                                        i.start()
                                    else:
                                        dictList = []
                                        [dictList.extend([k, v]) for k, v in my_dict.items()]
                                        Position = dictList.index(x) - 1
                                        message = ('\n' + "Received message from -> " + dictList[
                                            Position] + " -> " + recv_data)
                                        print(message)
                                        enter_func()
                                        # recv_data = sock.recv(1024).decode()
                                success = False
                            except Exception as e:
                                error_log(e)
                except Exception as e:
                    print(e)


class Check(Thread):
    def __init__(self):
        global done

        global back
        global message
        global dict

        global new_client
        global replacing_dict
        Thread.__init__(self)
        print("SYSTEM: Check initialized")

    def run(self):
        global new_client
        global dict
        global done
        global replacing_dict
        print("SYSTEM: Check started")
        while True:
            i = 0
            if dict != "":
                for x in dict:
                    if str(x).__contains__("\n"):
                        replacing_dict = False
                        print('replacing dict')
                        oldkey = x
                        old_value = dict[x]
                        del dict[x]
                        new_x = str(x).split("\n")[0]
                        print(new_x)
                        if new_x == "":
                            print('switching')
                            new_x = str(x).split("\n")[1]
                        dict[new_x] = old_value
                        replacing_dict = True
            while i < len(dict):
                time.sleep(.5)
                if len(dict) != 0:
                    try:
                        soc = list(dict.values())[i]
                        message = "--TEST--"
                    except:
                        print('index error. Resetting check')
                        i = 0
                    try:

                        soc.send(message.encode("utf-8"))
                    except:
                        # new_client = False
                        print(dict)
                        print('closing connection to ' +
                              str(list(dict.keys())[i]))
                        key = list(dict.keys())[i]
                        sock = list(dict.values())[i]
                        del dict[key]
                        print(dict)
                        try:
                            if not str(sock).__contains__('[closed]'):
                                sel.unregister(sock)
                                sock.close()
                                i = 0
                        except:
                            print('unable to close sock' + str(sock))
                        if in_messaging is True:
                            back_func()
                        else:
                            enter_func()
                    i += 1


class BackupThread(Thread):
    def __init__(self, backup_pc):
        Thread.__init__(self)
        self.backup_pc = backup_pc

    def run(self):
        backup_func(self.backup_pc)


class OtherBackupThread(Thread):
    def __init__(self, user_input, pc_socket):
        Thread.__init__(self)
        self.pc_socket = pc_socket
        self.user_input = user_input

    def run(self):
        write_backup_files(self.user_input, self.pc_socket)


class SendToThread(Thread):
    def __init__(self, Q, x):
        Thread.__init__(self)
        self.Q = Q
        self.x = x

    def run(self):
        send_to_func(self.Q, self.x)


class GetThread(Thread):
    def __init__(self, s):
        Thread.__init__(self)
        self.sock = get_ip_from_sock(s)

    def run(self):
        Get.main(self.sock)


def create_resource_file(file_name, print_text):
    if os.path.isfile("Resources\\" + file_name):
        pass
    else:
        print("SYSTEM: Creating " + print_text + "...")
        with open("Resources\\" + file_name, "w+") as file_to_create:
            pass


def globalize_computer_name(RCN, M):
    global rcn
    global MAC
    rcn = RCN
    MAC = M
    print(RCN)
    print(MAC)


def start_the_rest_of_the_classes():
    d.start()
    b.start()


if __name__ == '__main__':
    try:
        received_computer_name = ""
        create_resource_file("ErrorLog.txt", "Error Log")
        create_resource_file("Profiles.txt", "Profile database")
        create_resource_file("IP.txt", "IP database")
        create_resource_file("Backup.txt", "Backup database")

        a = Starter()
        get_ip_addresses_func()
        b = Send()
        c = Receive()
        d = Check()
        a.start()

        if connected is True:
            started = True

        start_the_rest_of_the_classes()

    except Exception as e:
        print(e)
        error_log(e)
