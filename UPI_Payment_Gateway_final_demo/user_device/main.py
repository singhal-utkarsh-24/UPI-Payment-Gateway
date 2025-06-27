
import sys
import os
import time
import threading
import json
import uuid


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_device.network import UserDeviceNetwork
from user_device.payment_parser import parse_payment_data
from common.network_protocol import Message
from common.constants import NETWORK

class UserDevice:
    def __init__(self):
        self.network = UserDeviceNetwork()
        self.current_user = None
        self.current_payment_data = None
        
        
        self.network.register_handler("PAYMENT_ACKNOWLEDGMENT", self.handle_payment_acknowledgment)
        self.network.register_handler("AUTHENTICATE_USER_RESPONSE", self.handle_authentication_response)
        self.network.register_handler("PROCESS_TRANSACTION_RESPONSE", self.handle_transaction_response)
    
    def start(self):
        
        print("Starting User Device...")
        
        
        self.network.start_server()
        
        print("User Device is running!")
        print("Type 'help' for commands.")
        
        try:
            while True:
                command = input("> ")
                
                if command.lower() == 'exit':
                    break
                
                if command.lower() == 'help':
                    self.print_help()
                
                elif command.lower() == 'login':
                    self.login_user()
                
                elif command.lower() == 'process':
                    self.process_payment()
                
                elif command.lower() == 'status':
                    self.check_status()
                
                elif command.lower() == 'logout':
                    self.logout_user()
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\nShutting down User Device...")
        finally:
            self.network.stop()
    
    def print_help(self):
        
        print("User Device Commands:")
        print("  login   - Login with UID and password")
        print("  process - Process a payment")
        print("  status  - Check status of last transaction")
        print("  logout  - Logout current user")
        print("  exit    - Exit the application")
        print("  help    - Show this help message")
    
    def login_user(self):
        
        if self.current_user:
            print("Already logged in. Please logout first.")
            return
        
        uid = input("Enter UID: ")
        password = input("Enter password: ")
        
        
        auth_message = Message(
            message_type="AUTHENTICATE_USER",
            sender="USER_DEVICE",
            receiver="BANK_SERVER",
            data={"uid": uid, "password": password},
            message_id=str(uuid.uuid4())
        )
        
        response = self.network.send_message(
            NETWORK["BANK_SERVER_HOST"],
            NETWORK["BANK_SERVER_PORT"],
            auth_message
        )
        
        if response:
            self.handle_authentication_response(response)
        else:
            print("Authentication failed: No response from server")

    def handle_authentication_response(self, message):
        
        if message.data.get("success"):
            self.current_user = {
                "user_id": message.data.get("user_id"),
                "mmid": message.data.get("mmid", "Unknown")
            }
            print(f"Successfully logged in. User ID: {self.current_user['user_id']}")
        else:
            print(f"Authentication failed: {message.data.get('error', 'Unknown error')}")
        
        return None  
    
    def logout_user(self):
        
        if not self.current_user:
            print("No user is currently logged in.")
            return
        
        print(f"Logging out user: {self.current_user['user_id']}")
        self.current_user = None
    
    def process_payment(self):
        
        if not self.current_user:
            print("Please login first.")
            return
        
        
        payment_data_str = input("Enter payment data: ")
        
        
        try:
            payment_data = parse_payment_data(payment_data_str)
            
            if not payment_data:
                print("Invalid payment data.")
                return
            
            print("\nPayment Details:")
            vmid = payment_data.get('vmid')
            timestamp = payment_data.get('timestamp')
            print(f"Virtual Merchant ID: {vmid}")
            print(f"Timestamp: {timestamp}")
            print(f"Amount: {payment_data.get('amount', 'Not specified')}")
            print(f"Description: {payment_data.get('desc', 'Not provided')}")
            
            
            amount = payment_data.get('amount')
            if not amount:
                amount = input("Enter amount to pay: ")
            
            
            pin = input("\nEnter your PIN to confirm payment: ")
            pin = str(pin)
            
            pin_verify_message = Message(
                message_type="VERIFY_PIN",
                sender="USER_DEVICE",
                receiver="BANK_SERVER",
                data={
                    "user_id": self.current_user["user_id"],
                    "pin": pin
                },
                message_id=str(uuid.uuid4())
            )

            pin_response = self.network.send_message(
                NETWORK["BANK_SERVER_HOST"],
                NETWORK["BANK_SERVER_PORT"],
                pin_verify_message
            )

            if not pin_response or not pin_response.data.get("success"):
                print("Payment cancelled: Incorrect PIN")
                return
            
            
            transaction_message = Message(
                message_type="PROCESS_TRANSACTION_REQUEST",
                sender="USER_DEVICE",
                receiver="UPI_MACHINE",
                data={
                    "vmid": vmid,
                    "timestamp": payment_data.get("timestamp"),
                    "amount": float(amount),
                    "desc": payment_data.get("desc", "Payment via UPI"),
                    "sender_id": self.current_user["user_id"]
                },
                message_id=str(uuid.uuid4())
            )
            
            print("Sending transaction request to UPI Machine...")
            print(f"Transaction data: vmid={vmid}, timestamp={payment_data.get('timestamp')}")
            response = self.network.send_message(
                NETWORK["UPI_MACHINE_HOST"],
                NETWORK["UPI_MACHINE_PORT"],
                transaction_message
            )
            
            if response:
                transaction_success = self.handle_transaction_response(response)
                
                if transaction_success:
                    
                    self.current_payment_data = {
                        "transaction_id": response.data.get("transaction_id"),
                        "amount": amount,
                        "merchant_id": vmid  
                    }
                    
                    
                    self.notify_merchant(True)
                else:
                    
                    self.notify_merchant(False)
            else:
                print("Transaction failed: No response from UPI machine")
                
        except Exception as e:
            print(f"Error processing payment: {e}")
    
    def handle_transaction_response(self, message):
        
        if message.data.get("success"):
            print(f"Transaction successful! Transaction ID: {message.data.get('transaction_id')}")
            return True
        else:
            print(f"Transaction failed: {message.data.get('error', 'Unknown error')}")
            return False

    
    def notify_merchant(self, success):
        
        if not self.current_payment_data and success:
            return
        
        
        notification_message = Message(
            message_type="PAYMENT_CONFIRMATION",
            sender="USER_DEVICE",
            receiver="UPI_MACHINE",
            data={
                "transaction_id": self.current_payment_data.get("transaction_id") if success else None,
                "amount": self.current_payment_data.get("amount") if success else None,
                "status": "SUCCESSFUL" if success else "FAILED"
            },
            message_id=str(uuid.uuid4())
        )
        
        response = self.network.send_message(
            NETWORK["UPI_MACHINE_HOST"],
            NETWORK["UPI_MACHINE_PORT"],
            notification_message
        )
        
        if response:
            print(f"Merchant notified of {'successful' if success else 'failed'} payment.")
        else:
            print(f"Warning: Could not notify merchant of {'successful' if success else 'failed'} payment.")

    def handle_payment_acknowledgment(self, message):
        
        print(f"Received acknowledgment from merchant: {message.data.get('status')}")
        return None  
    
    def check_status(self):
        
        if not self.current_payment_data:
            print("No recent transactions.")
            return
        
        print("\nLast Transaction:")
        print(f"Transaction ID: {self.current_payment_data['transaction_id']}")
        print(f"Amount: {self.current_payment_data['amount']}")
        print(f"Merchant ID: {self.current_payment_data['merchant_id']}")
        print("Status: Completed")

if __name__ == "__main__":
    user_device = UserDevice()
    user_device.start()
