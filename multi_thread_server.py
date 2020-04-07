# import socket programming library
import socket
import json
import os
import shutil
import pickle

# import thread module
from _thread import *
import threading


config_data = None


class Error(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


BAD_SEQUENCE_OF_COMMANDS = '503 Bad sequence of commands.'
INVALID_USERNAME_PASSWORD = '403 Invalid username or password.'
USERNAME_OK = '331 User name okey, need password.'
LOGIN_OK = '230 User logged in, proceed.'
NOT_AUTHORIZED = '332 Need account for login.'
MAX_SIZE = 1024
SYNTAX_ERROR = '501 Syntax error in parameters or arguments.'
FILE_EXISTED = '500 File or directory already existed in this path.'
FILE_NOT_EXISTED = '500 File or directory not existed in this path.'
NOT_DIRECTOR = '500 Not a directory.'
LIST_TRANSFER_DONE = '226 List transfer done.'
CWD_SUCCESS = '250 Successful Change.'


# print_lock = threading.Lock()

# thread function

class Client_handler:
    def __init__(self, client):
        self.base_dir = os.getcwd
        self.curr_dir = self.base_dir
        self.logged_in = True
        self.username = None
        self.user = None
        self.client = client

    def validate_arg(self, arg):
        if arg[0] != '<' or arg[len(arg) - 1] != '>':
            raise Error(SYNTAX_ERROR)

    def receive_data_from_client(self):
        return (self.client.recv(MAX_SIZE)).decode()

    def end_connection(self, data):
        if not data:
            return True
        return False

    def check_for_previous_username(self):
        if self.username:
            raise Error(BAD_SEQUENCE_OF_COMMANDS)

    def get_neat_data(self, arg):
        return arg[1:len(arg) - 1]

    def send_message(self, message):
        self.client.send(message.encode())

    def close_connection(self):
        self.client.close()

    def check_for_existing_username(self):
        if not self.username or self.logged_in:
            raise Error(BAD_SEQUENCE_OF_COMMANDS)

    def handle_USER_command(self, arg):
        self.check_for_previous_username()
        self.validate_arg(arg[1])
        username = self.get_neat_data(arg[1])
        self.user = Utils().find_user(username)
        self.username = self.user['user']
        self.send_message(USERNAME_OK)

    def validate_password(self, password):
        if password != self.user['password']:
            raise Error(INVALID_USERNAME_PASSWORD)

    def handle_PASS_command(self, arg):
        self.check_for_existing_username()
        self.validate_arg(arg[1])
        password = self.get_neat_data(arg[1])
        self.validate_password(password)
        self.logged_in = True
        self.send_message(LOGIN_OK)


class Utils:
    def get_diff_path(self, base_dir, curr_dir):
        base_dir_list = base_dir.split('/')
        curr_dir_list = curr_dir.split('/')
        result_dir_list = []
        for path in curr_dir_list:
            if path not in base_dir_list:
                result_dir_list.append(path)
        result_dir = '/'.join(result_dir_list)
        if result_dir:
            return result_dir + '/'
        return result_dir

    def read_config_file(self):
        global config_data
        config_file = open('config.json')
        config_data = json.load(config_file)

    def get_users(self):
        return config_data['users']

    def find_user(self, user_name):
        for user in self.get_users():
            if user['user'] == user_name:
                return user
        raise Error(INVALID_USERNAME_PASSWORD)

    def get_parsed_data(self, data):
        return list(map(str, data.split()))

    def get_command(self, data):
        return data[0]


def threaded(client_handler):
    while True:

        # data received from client
        received_data = client_handler.receive_data_from_client()

        if (client_handler.end_connection(received_data)):
            print('Bye')
            break

        parsed_data = Utils().get_parsed_data(received_data)

        command = Utils().get_command(parsed_data)

        try:
            if command == 'USER':
                client_handler.handle_USER_command(parsed_data)
                continue
            elif command == 'PASS':
                client_handler.handle_PASS_command(parsed_data)

        except Error as e:
            client_handler.send_message(e.message)
            continue

        # # if (not logged_in) and (parsed_data[0] not in ['USER', 'PASS']):
        # #     c.send(NOT_AUTHORIZED.encode())
        # #     continue
        # # if (not logged_in) and (parsed_data[0] in ['USER', 'PASS']):
        # #     if not user_username:
        # #         if parsed_data[0] != 'USER':
        # #             c.send(BAD_SEQUENCE_OF_COMMANDS.encode())
        # #             continue
        # #         if parsed_data[1][0] != '<' or parsed_data[1][len(parsed_data[1]) - 1] != '>':
        # #             c.send(SYNTAX_ERROR.encode())
        # #             continue
        # #         input_username = parsed_data[1][1:len(parsed_data[1]) - 1]
        # #         user = find_user(input_username)
        # #         if not user:
        # #             c.send(INVALID_USERNAME_PASSWORD.encode())
        # #             continue
        # #         user_username = user['user']
        # #         c.send(USERNAME_OK.encode())
        # #         continue
        # #     else:
        # #         if parsed_data[0] != 'PASS':
        # #             c.send(BAD_SEQUENCE_OF_COMMANDS.encode())
        # #             continue
        # #         if parsed_data[1][0] != '<' or parsed_data[1][len(parsed_data[1]) - 1] != '>':
        # #             c.send(SYNTAX_ERROR.encode())
        # #             continue
        # #         input_password = parsed_data[1][1:len(parsed_data[1]) - 1]
        # #         if input_password != user['password']:
        # #             c.send(INVALID_USERNAME_PASSWORD.encode())
        # #             continue
        # #         c.send(LOGIN_OK.encode())
        # #         logged_in = True
        # #         continue
        # if(logged_in):
        #     if parsed_data[0] == 'PWD':
        #         c.send(('257 <' + curr_dir + '>').encode())
        #         continue
        #     if parsed_data[0] == 'MKD':
        #         if len(parsed_data) == 2:
        #             if parsed_data[1][0] != '<' or parsed_data[1][len(parsed_data[1]) - 1] != '>':
        #                 c.send(SYNTAX_ERROR.encode())
        #                 continue
        #             dir_name = parsed_data[1][1:len(parsed_data[1]) - 1]
        #             if os.path.exists(dir_name):
        #                 c.send(FILE_EXISTED.encode())
        #                 continue
        #             os.mkdir(dir_name)
        #             c.send(('257 <' + dir_name + '> created.').encode())
        #             continue

        #         elif len(parsed_data) == 3:
        #             if parsed_data[1] != '-i':
        #                 print('1')
        #                 c.send(SYNTAX_ERROR.encode())
        #                 continue
        #             if parsed_data[2][0] != '<' or parsed_data[2][len(parsed_data[2]) - 1] != '>':
        #                 print(2)
        #                 c.send(SYNTAX_ERROR.encode())
        #                 continue
        #             file_name = parsed_data[2][1:len(parsed_data[2]) - 1]
        #             if os.path.exists(file_name):
        #                 c.send(FILE_EXISTED.encode())
        #                 continue
        #             open(file_name, 'w+').close()
        #             c.send(('257 <' + file_name + '> created.').encode())
        #             continue
        #     if parsed_data[0] == 'RMD':
        #         if len(parsed_data) == 2:
        #             if parsed_data[1][0] != '<' or parsed_data[1][len(parsed_data[1]) - 1] != '>':
        #                 c.send(SYNTAX_ERROR.encode())
        #                 continue
        #             file_name = parsed_data[1][1:len(parsed_data[1]) - 1]
        #             if not os.path.exists(file_name):
        #                 c.send(FILE_NOT_EXISTED.encode())
        #                 continue
        #             os.remove(file_name)
        #             c.send(('257 <' + file_name + '> deleted.').encode())
        #             continue

        #         elif len(parsed_data) == 3:
        #             if parsed_data[1] != '-f':
        #                 c.send(SYNTAX_ERROR.encode())
        #                 continue
        #             if parsed_data[2][0] != '<' or parsed_data[2][len(parsed_data[2]) - 1] != '>':
        #                 c.send(SYNTAX_ERROR.encode())
        #                 continue
        #             dir_name = parsed_data[2][1:len(parsed_data[2]) - 1]
        #             if not os.path.exists(dir_name):
        #                 c.send(FILE_NOT_EXISTED.encode())
        #                 continue
        #             shutil.rmtree(dir_name)
        #             c.send(('257 <' + dir_name + '> deleted.').encode())
        #             continue
        #     if parsed_data[0] == 'LIST':
        #         data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #         data_socket.connect(('', int(parsed_data[1])))
        #         diff_path = get_diff_path(base_dir, curr_dir)
        #         if not diff_path:
        #             data_socket.send(pickle.dumps(os.listdir()))
        #         else:
        #             data_socket.send(pickle.dumps(os.listdir(diff_path)))
        #         data_socket.close()
        #         c.send(LIST_TRANSFER_DONE.encode())
        #         continue
        #     if parsed_data[0] == 'CWD':
        #         if parsed_data[1][0] != '<' or parsed_data[1][len(parsed_data[1]) - 1] != '>':
        #             c.send(SYNTAX_ERROR.encode())
        #             continue
        #         target_dir = parsed_data[1][1:len(parsed_data[1]) - 1]
        #         if not target_dir:
        #             curr_dir = base_dir
        #             c.send(CWD_SUCCESS.encode())
        #             continue
        #         elif target_dir == '..':
        #             if base_dir != curr_dir:
        #                 curr_dir_list = curr_dir.split('/')
        #                 curr_dir_list.pop()
        #                 curr_dir = '/'.join(curr_dir_list)
        #             c.send(CWD_SUCCESS.encode())
        #             continue
        #         else:
        #             diff_path = get_diff_path(base_dir, curr_dir)
        #             print(diff_path + target_dir)
        #             if os.path.isdir(diff_path + target_dir):
        #                 curr_dir += '/' + target_dir
        #                 c.send(CWD_SUCCESS.encode())
        #                 continue
        #             else:
        #                 c.send(NOT_DIRECTOR.encode())
        #                 continue

    client_handler.close_connection()


def Main():

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    print("socket binded to port", port)

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:

        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client
        # print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(threaded, (Client_handler(c),))
    s.close()


if __name__ == '__main__':
    Utils().read_config_file()
    Main()
