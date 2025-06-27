
import sys
import os
import time
import threading
import uuid


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from upi_machine.network import UPIMachineNetwork
from upi_machine.qr_generator import generate_payment_data, generate_qr_code, save_data_to_file, save_qr_to_file, decrypt_vmid_to_mid
from common.network_protocol import Message
from common.constants import NETWORK

class UPIMachine:
    def __init__(self):
        self.network = UPIMachineNetwork()
        self.current_merchant_id = None
        self.current_vmid = None
        self.current_transaction = None
        
        
        self.network.register_handler("PAYMENT_CONFIRMATION", self.handle_payment_confirmation)
        self.network.register_handler("PROCESS_TRANSACTION_REQUEST", self.handle_transaction_request)
    
    def start(self):
        
        print("Starting UPI Machine...")
        
        
        self.network.start_server()
        
        
        from bank_server.bank_manager import BankManager
        bank_manager = BankManager()
        bank_manager.initialize()
        
        print("UPI Machine is running!")
        print("Enter merchant ID or 'exit' to quit:")
        
        try:
            while True:
                command = input("> ")
                
                if command.lower() == 'exit':
                    break
                
                if command.lower() == 'help':
                    self.print_help()
                    continue
                
                
                self.set_merchant_id(command)
                
                
                if self.current_merchant_id:
                    self.payment_menu()
        
        except KeyboardInterrupt:
            print("\nShutting down UPI Machine...")
        finally:
            self.network.stop()
    
    def print_help(self):
        
        print("UPI Machine Commands:")
        print("  <merchant_id> - Set the current merchant ID")
        print("  exit         - Exit the application")
        print("  help         - Show this help message")
    
    def set_merchant_id(self, merchant_id):
        
        print(f"Setting merchant ID to: {merchant_id}")
        
        
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from bank_server.bank_manager import BankManager
        
        
        bank_manager = BankManager()
        bank_manager.initialize()
        
        
        # print("Available merchants in the system:")
        # if bank_manager.merchants:
        #     for mid, merchant in bank_manager.merchants.items():
        #         print(f"  {mid}: {merchant.name}")
        # else:
        #     print("  No merchants registered in the system")
        
        
        self.current_merchant_id = merchant_id
        self.current_vmid = None  
    
    def payment_menu(self):
        
        while self.current_merchant_id:
            print("\nPayment Options:")
            print("1. Generate payment data for any amount")
            print("2. Generate payment data for specific amount")
            print("3. Generate QR code for any amount")
            print("4. Generate QR code for specific amount")
            print("5. Check transaction status")
            print("6. Change merchant")
            print("7. Back to main menu")
            
            choice = input("Select an option (1-7): ")
            
            if choice == '1':
                self.generate_payment_data()
            elif choice == '2':
                self.generate_payment_data_with_amount()
            elif choice == '3':
                self.generate_qr_code()
            elif choice == '4':
                self.generate_qr_code_with_amount()
            elif choice == '5':
                self.check_transaction_status()
            elif choice == '6':
                self.current_merchant_id = None
                print("Merchant ID cleared. Enter a new merchant ID:")
                return
            elif choice == '7':
                self.current_merchant_id = None
                return
            else:
                print("Invalid option. Please try again.")
    
    def generate_payment_data(self):
        
        payment_data, vmid = generate_payment_data(self.current_merchant_id)
        self.current_vmid = vmid
        
        filename = f"payment_{self.current_merchant_id}_{int(time.time())}.txt"
        save_data_to_file(payment_data, filename)
        
        print(f"Payment data generated and saved as {filename}")
        print(f"VMID generated: {vmid}")
        print("Payment data (copy this to the user device):")
        print("-" * 40)
        print(payment_data)
        print("-" * 40)
        print("Waiting for payment confirmation...")
    
    def generate_payment_data_with_amount(self):
        
        try:
            amount = float(input("Enter amount: "))
            description = input("Enter description (optional): ")
            
            payment_data, vmid = generate_payment_data(
                self.current_merchant_id, 
                amount=amount,
                description=description if description else None
            )
            self.current_vmid = vmid
            
            filename = f"payment_{self.current_merchant_id}_{int(time.time())}.txt"
            save_data_to_file(payment_data, filename)
            
            print(f"Payment data generated and saved as {filename}")
            print(f"VMID generated: {vmid}")
            print("Payment data (copy this to the user device):")
            print("-" * 40)
            print(payment_data)
            print("-" * 40)
            print("Waiting for payment confirmation...")
            
        except ValueError:
            print("Invalid amount. Please enter a valid number.")
    
    def generate_qr_code(self):
        
        try:
            payment_data, vmid = generate_payment_data(self.current_merchant_id)
            self.current_vmid = vmid
            
            qr_data = generate_qr_code(payment_data)
            
            filename = f"qr_{self.current_merchant_id}_{int(time.time())}.png"
            save_qr_to_file(qr_data, filename)
            
            print(f"QR code generated and saved as {filename}")
            print(f"VMID generated: {vmid}")
            print("Scan this QR code with the user device")
            print("Waiting for payment confirmation...")
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            print("Using text-based payment data instead:")
            self.generate_payment_data()
    
    def generate_qr_code_with_amount(self):
        
        try:
            amount = float(input("Enter amount: "))
            description = input("Enter description (optional): ")
            
            payment_data, vmid = generate_payment_data(
                self.current_merchant_id, 
                amount=amount,
                description=description if description else None
            )
            self.current_vmid = vmid
            
            qr_data = generate_qr_code(payment_data)
            
            filename = f"qr_{self.current_merchant_id}_{int(time.time())}.png"
            save_qr_to_file(qr_data, filename)
            
            print(f"QR code generated and saved as {filename}")
            print(f"VMID generated: {vmid}")
            print("Scan this QR code with the user device")
            print("Waiting for payment confirmation...")
            
        except ValueError:
            print("Invalid amount. Please enter a valid number.")
        except Exception as e:
            print(f"Error generating QR code: {e}")
            print("Using text-based payment data instead:")
            self.generate_payment_data_with_amount()
    
    def check_transaction_status(self):
        
        if not self.current_transaction:
            print("No active transaction.")
            return
        
        
        print(f"Transaction {self.current_transaction}: Pending")
    
    def handle_payment_confirmation(self, message):
        
        print("\nPayment confirmation received!")
        print(f"Transaction ID: {message.data.get('transaction_id')}")
        print(f"Amount: {message.data.get('amount')}")
        print(f"Status: {message.data.get('status')}")
        
        self.current_transaction = message.data.get('transaction_id')
        
        
        return Message(
            message_type="PAYMENT_ACKNOWLEDGMENT",
            sender="UPI_MACHINE",
            receiver=message.sender,
            data={"status": "received"},
            message_id=message.message_id
        )
    
    def handle_transaction_request(self, message):
        
        print("\nTransaction request received from user device")
        
        
        vmid = message.data.get('vmid')
        timestamp = int(message.data.get('timestamp', 0))
        amount = message.data.get('amount')
        description = message.data.get('desc', 'Payment via UPI')
        sender_id = message.data.get('sender_id')
        
        print(f"Processing payment with VMID: {vmid}")
        print(f"Timestamp: {timestamp}")
        print(f"Amount: {amount}")
        print(f"Sender ID: {sender_id}")
        
        if not vmid or not amount or not sender_id:
            print("Error: Missing required transaction data")
            return Message(
                message_type="PROCESS_TRANSACTION_RESPONSE",
                sender="UPI_MACHINE",
                receiver=message.sender,
                data={
                    "success": False,
                    "error": "Missing required transaction data"
                },
                message_id=message.message_id
            )
        
        
        from bank_server.bank_manager import BankManager
        bank_manager = BankManager()
        bank_manager.initialize()
        
        print("Available merchants before decryption:")
        if bank_manager.merchants:
            for mid, merchant in bank_manager.merchants.items():
                print(f"  {mid}: {merchant.name}")
        else:
            print("  No merchants registered in the system")
        
        
        merchant_id = decrypt_vmid_to_mid(vmid, timestamp)
        
        if not merchant_id:
            print(f"Error: Failed to decrypt VMID {vmid}")
            return Message(
                message_type="PROCESS_TRANSACTION_RESPONSE",
                sender="UPI_MACHINE",
                receiver=message.sender,
                data={
                    "success": False,
                    "error": "Invalid merchant ID"
                },
                message_id=message.message_id
            )
        
        print(f"Decrypted VMID {vmid} to Merchant ID {merchant_id}")
        
        
        if merchant_id in bank_manager.merchants:
            print(f"Merchant found: {bank_manager.merchants[merchant_id].name}")
        else:
            print(f"Warning: Merchant ID {merchant_id} not found in the system after decryption")
        
        
        transaction_message = Message(
            message_type="PROCESS_TRANSACTION",
            sender="UPI_MACHINE",
            receiver="BANK_SERVER",
            data={
                "sender_id": sender_id,
                "receiver_id": merchant_id,
                "amount": float(amount),
                "description": description
            },
            message_id=str(uuid.uuid4())
        )
        
        print("Forwarding transaction request to bank server...")
        print(f"Data: sender_id={sender_id}, receiver_id={merchant_id}")
        print(f"Data: amount={amount}, description={description}")
        response = self.network.send_message(
            NETWORK["BANK_SERVER_HOST"],
            NETWORK["BANK_SERVER_PORT"],
            transaction_message
        )
        
        if not response:
            print("Error: No response from bank server")
            return Message(
                message_type="PROCESS_TRANSACTION_RESPONSE",
                sender="UPI_MACHINE",
                receiver=message.sender,
                data={
                    "success": False,
                    "error": "Bank server not responding"
                },
                message_id=message.message_id
            )
        
        
        if response.data.get("success"):
            self.current_transaction = response.data.get("transaction_id")
            print(f"Transaction successful! ID: {self.current_transaction}")
        else:
            error_msg = response.data.get("error", "Unknown error")
            print(f"Transaction failed: {error_msg}")
        
        
        return Message(
            message_type="PROCESS_TRANSACTION_RESPONSE",
            sender="UPI_MACHINE",
            receiver=message.sender,
            data=response.data,
            message_id=message.message_id
        )

if __name__ == "__main__":
    upi_machine = UPIMachine()
    upi_machine.start()
 