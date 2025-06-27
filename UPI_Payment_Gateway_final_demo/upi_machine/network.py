
import socket
import json
import threading
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.network_protocol import Message
from common.constants import NETWORK

class UPIMachineNetwork:
    def __init__(self):
        self.host = NETWORK["UPI_MACHINE_HOST"]
        self.port = NETWORK["UPI_MACHINE_PORT"]
        self.socket = None
        self.connected = False
        self.message_handlers = {}
    
    def start_server(self):
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.connected = True
        print(f"UPI Machine server started on {self.host}:{self.port}")
        
        
        threading.Thread(target=self._accept_connections, daemon=True).start()
    
    def _accept_connections(self):
        
        while self.connected:
            try:
                client_socket, client_address = self.socket.accept()
                print(f"Connection from {client_address}")
                threading.Thread(target=self._handle_client, 
                                args=(client_socket,), daemon=True).start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
                if not self.connected:
                    break
    
    def _handle_client(self, client_socket):
        
        try:
            
            data = b""
            while self.connected:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                
                try:
                    
                    message = Message.from_json(data.decode())
                    
                    
                    self._process_message(message, client_socket)
                    
                    
                    data = b""
                except (json.JSONDecodeError, UnicodeDecodeError):
                    
                    continue
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def _process_message(self, message, client_socket):
        
        print(f"Received message: {message.message_type}")
        
        if message.message_type in self.message_handlers:
            response = self.message_handlers[message.message_type](message)
            if response:
                client_socket.sendall(response.to_json().encode())
        else:
            print(f"No handler for message type: {message.message_type}")
    
    def register_handler(self, message_type, handler_function):
        
        self.message_handlers[message_type] = handler_function
    
    def send_message(self, host, port, message):
        
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            client_socket.sendall(message.to_json().encode())
            
            
            response_data = client_socket.recv(4096)
            client_socket.close()
            
            if response_data:
                return Message.from_json(response_data.decode())
            return None
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def stop(self):
        
        self.connected = False
        if self.socket:
            self.socket.close()
