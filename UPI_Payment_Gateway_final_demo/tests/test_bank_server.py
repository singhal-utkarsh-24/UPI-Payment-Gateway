import sys
import os
import unittest
import threading
import time
import socket


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bank_server.main import BankServer
from common.network_protocol import Message
from common.constants import NETWORK

class TestBankServer(unittest.TestCase):
    
    def setUp(self):
        
        self.bank_server = BankServer()
        
        
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        
        time.sleep(1)
    
    def start_server(self):
        
        try:
            self.bank_server.network.start_server()
            self.bank_server.bank_manager.initialize()
            
            
            time.sleep(10)  
        except KeyboardInterrupt:
            self.bank_server.network.stop()
    
    def test_server_startup(self):
        
        
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((NETWORK["BANK_SERVER_HOST"], NETWORK["BANK_SERVER_PORT"]))
            client_socket.close()
            connected = True
        except:
            connected = False
        
        self.assertTrue(connected, "Failed to connect to the Bank Server")
    
    def test_user_registration(self):
        
        
        registration_message = Message(
            message_type="REGISTER_USER",
            sender="TEST_CLIENT",
            receiver="BANK_SERVER",
            data={
                "name": "Network Test User",
                "bank_code": "SBIN0000001",
                "account_number": "123456789",
                "pin": "1234"
            },
            message_id="test123"
        )
        
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((NETWORK["BANK_SERVER_HOST"], NETWORK["BANK_SERVER_PORT"]))
        client_socket.sendall(registration_message.to_json().encode())
        
        
        response_data = client_socket.recv(4096)
        client_socket.close()
        
        
        response = Message.from_json(response_data.decode())
        
        
        self.assertEqual(response.message_type, "REGISTER_USER_RESPONSE")
        self.assertEqual(response.sender, "BANK_SERVER")
        self.assertEqual(response.receiver, "TEST_CLIENT")
        self.assertEqual(response.message_id, "test123")
        self.assertTrue(response.data["success"])
        self.assertIsNotNone(response.data["user_id"])

    def tearDown(self):
        
        self.bank_server.network.stop()

if __name__ == "__main__":
    unittest.main()
