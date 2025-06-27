
import sys
import os
import threading
import time
import hashlib
from quantum_crypto import demonstrate_pin_vulnerability, crack_pin
from crypto import generate_sha256_hash
import random



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bank_server.bank_manager import BankManager
from bank_server.network import BankServerNetwork
from common.network_protocol import Message
from common.constants import NETWORK

class BankServer:
    def __init__(self):
        self.bank_manager = BankManager()
        self.network = BankServerNetwork()
        
        
        self.network.register_handler("REGISTER_USER", self.handle_register_user)
        self.network.register_handler("REGISTER_MERCHANT", self.handle_register_merchant)
        self.network.register_handler("AUTHENTICATE_USER", self.handle_authenticate_user)
        self.network.register_handler("PROCESS_TRANSACTION", self.handle_process_transaction)
        self.network.register_handler("GET_MERCHANT_INFO", self.handle_get_merchant_info)
        self.network.register_handler("VERIFY_PIN", self.handle_verify_pin)
        
    def start(self):
        
        print("Starting Bank Server...")
        
        
        self.network.start_server()
        
        
        self.bank_manager.initialize()
        
        print("Bank Server is running!")
        print("Type 'help' for available commands.")
        
        try:
            while True:
                command = input("bank> ").strip().lower()
                
                if command == "exit":
                    break
                elif command == "help":
                    self.print_help()
                elif command == "register user":
                    self.register_user_command()
                elif command == "register merchant":
                    self.register_merchant_command()
                elif command == "list users":
                    self.list_users()
                elif command == "list merchants":
                    self.list_merchants()
                # elif command == "verify blockchain":
                #     self.verify_blockchain_command()
                elif command == "show blockchain":
                    self.show_blockchain_command()
                # elif command == "audit":
                #     self.run_security_audit()
                elif command == "register_bank":
                    self.register_bank_command()
                elif command == "list_banks":
                    self.list_banks()
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
        except KeyboardInterrupt:
            print("\nShutting down Bank Server...")
        finally:
            self.network.stop()

    def generate_sha256_hash(input_str: str) -> str:
        
        hash_object = hashlib.sha256(input_str.encode())
        hex_dig = hash_object.hexdigest()
        return hex_dig[:16]  

    def print_help(self):
        
        print("\nBank Server Commands:")
        print("  register user     - Register a new user")
        print("  register merchant - Register a new merchant")
        print("  list users        - Display all registered users")
        print("  list merchants    - Display all registered merchants")
        # print("  verify blockchain - Verify blockchain integrity")
        print("  show blockchain   - Display blockchain for a bank")
        # print("  Vulnerability test- Run PIN vulnerability test")
        print("  exit              - Shutdown the server")
        print("  help              - Display this help message")
        # print("  register_bank     - Register a new bank")
        print("  list_banks        - List all registered banks")
        print()
        
    def register_user_command(self):
        
        print("\n==== Register New User ====")
        name = input("Enter user name: ")
        
        
        print("\nAvailable Banks and Branches:")
        banks_by_name = {}
        for code, bank in self.bank_manager.banks.items():
            if bank.name not in banks_by_name:
                banks_by_name[bank.name] = []
            banks_by_name[bank.name].append(code)
        
        for bank_name, codes in banks_by_name.items():
            print(f"\n{bank_name}:")
            for i, code in enumerate(codes):
                branch = self.bank_manager.banks[code].branches[0]
                print(f"  {i+1}. {code}: {branch}")
        
        bank_code = input("\nEnter bank code: ")
        if bank_code not in self.bank_manager.banks:
            print(f"Error: Bank code '{bank_code}' not found.")
            return
        
        mobile_number = input("Enter mobile number: ")
        password = input("Enter password: ")
        
        pin = input("Enter 4-digit PIN for UPI transactions: ")
        if len(pin) != 4 or not pin.isdigit():
            print("Error: PIN must be exactly 4 digits.")
            return
        
        
        print("\n==== Checking PIN Security ====")
        pin_result = crack_pin(int(pin))
        if pin_result["success"]:
            print(f"WARNING: Your PIN {pin} is vulnerable to quantum attacks!")
            print(f"It can be factored into: {pin_result['factors']}")
            print(f"Time to crack: {pin_result['time_taken']:.4f} seconds")
            print("\nConsider choosing a more secure PIN.")
            
            change_pin = input("Would you like to choose a different PIN? (y/n): ")
            if change_pin.lower() == 'y':
                return self.register_user_command()  
        else:
            print(f"Your PIN appears to be quantum-resistant.")
        
        try:
            initial_balance = float(input("\nEnter initial account balance: "))
        except ValueError:
            print("Error: Initial balance must be a number.")
            return
        
        
        success, user_id = self.bank_manager.register_user(
            name=name,
            bank_code=bank_code,
            mobile_number=mobile_number,
            password=password,
            pin=pin,
            initial_balance=initial_balance
        )
        
        if success:
            user = self.bank_manager.users[user_id]
            print("\n==== Registration Successful ====")
            print(f"User Name: {user.name}")
            print(f"UID: {user.uid}")
            print(f"MMID: {user.mmid}")
            print(f"Mobile: {user.mobile_number}")
            print(f"PIN: {pin}")
            print(f"Initial Balance: {user.balance}")
            print("================================")
        else:
            print("Registration failed.")

    def register_merchant_command(self):
        
        print("\n==== Register New Merchant ====")
        name = input("Enter merchant name: ")
        
        
        print("\nAvailable Banks:")
        for code, bank in self.bank_manager.banks.items():
            print(f"  {code}: {bank.name}")
        
        bank_code = input("\nEnter bank code: ")
        if bank_code not in self.bank_manager.banks:
            print(f"Error: Bank code '{bank_code}' not found.")
            return
        
        
        password = input("Enter password to access account: ")
        
        try:
            initial_balance = float(input("Enter initial account balance: "))
        except ValueError:
            print("Error: Initial balance must be a number.")
            return
        
        success, merchant_id = self.bank_manager.register_merchant(
            name=name,
            bank_code=bank_code,
            
            password=password,
            initial_balance=initial_balance
        )
        
        if success:
            merchant = self.bank_manager.merchants[merchant_id]
            print("\n==== Registration Successful ====")
            print(f"Merchant Name: {merchant.name}")
            print(f"Merchant ID (MID): {merchant.mid}")
            print(f"Account Number: {merchant.account_number}")
            print(f"Initial Balance: {merchant.balance}")
            print("================================")
        else:
            print("Registration failed.")

    def list_users(self):
        
        if not self.bank_manager.users:
            print("No users registered.")
            return
        
        print("\n==== Registered Users ====")
        for uid, user in self.bank_manager.users.items():
            print(f"User ID: {uid}")
            print(f"Name: {user.name}")
            print(f"MMID: {user.mmid}")
            print(f"Bank: {user.bank_code}")
            print(f"Balance: {user.balance}")
            print("------------------------")
        print()

    def list_merchants(self):
        
        if not self.bank_manager.merchants:
            print("No merchants registered.")
            return
        
        print("\n==== Registered Merchants ====")
        for mid, merchant in self.bank_manager.merchants.items():
            print(f"Merchant ID: {mid}")
            print(f"Name: {merchant.name}")
            print(f"MID: {merchant.mid}")
            print(f"Bank: {merchant.bank_code}")
            print(f"Balance: {merchant.balance}")
            print("----------------------------")
        print()
    
    def handle_register_user(self, message):
        
        user_data = message.data
        success, user_id = self.bank_manager.register_user(
            name=user_data.get("name"),
            bank_code=user_data.get("bank_code"),
            mobile_number=user_data.get("mobile_number"),
            password=user_data.get("password"),
            pin=user_data.get("pin"),
            initial_balance=float(user_data.get("initial_balance", 0.0))
        )
        
        response_data = {
            "success": success,
            "user_id": user_id if success else None,
            "error": None if success else "Registration failed"
        }
        
        return Message(
            message_type="REGISTER_USER_RESPONSE",
            sender="BANK_SERVER",
            receiver=message.sender,
            data=response_data,
            message_id=message.message_id
        )

    
    def handle_register_merchant(self, message):
        
        merchant_data = message.data
        success, merchant_id = self.bank_manager.register_merchant(
            name=merchant_data.get("name"),
            bank_code=merchant_data.get("bank_code"),
            account_number=merchant_data.get("account_number"),
            password=merchant_data.get("password", ""),
            initial_balance=float(merchant_data.get("initial_balance", 0.0))
        )
        
        response_data = {
            "success": success,
            "merchant_id": merchant_id if success else None,
            "error": None if success else "Registration failed"
        }
        
        return Message(
            message_type="REGISTER_MERCHANT_RESPONSE",
            sender="BANK_SERVER",
            receiver=message.sender,
            data=response_data,
            message_id=message.message_id
        )


    def handle_authenticate_user(self, message):
        
        auth_data = message.data
        uid = auth_data.get("uid")
        password = auth_data.get("password")
        
        
        if uid:
            user = self.bank_manager.users.get(uid)
            if user:
                
                hashed_password = generate_sha256_hash(password)
                success = user.password == hashed_password
            else:
                success = False
                user = None
        else:
            
            mmid = auth_data.get("mmid")
            if mmid:
                success, user = self.bank_manager.authenticate_user(
                    mmid=mmid,
                    password=password
                )
            else:
                
                success = False
                user = None
        
        response_data = {
            "success": success,
            "user_id": user.uid if success else None,
            "mmid": user.mmid if success else None,
            "error": None if success else "Authentication failed"
        }
        
        return Message(
            message_type="AUTHENTICATE_USER_RESPONSE",
            sender="BANK_SERVER",
            receiver=message.sender,
            data=response_data,
            message_id=message.message_id
        )

    
    def handle_process_transaction(self, message):
        
        transaction_data = message.data
        print(f"Processing transaction: {transaction_data}")
        success, transaction_id_or_error = self.bank_manager.process_transaction(
            sender_id=transaction_data.get("sender_id"),
            receiver_id=transaction_data.get("receiver_id"),
            amount=float(transaction_data.get("amount")),
            description=transaction_data.get("description", "")
        )
        
        response_data = {
            "success": success,
            "transaction_id": transaction_id_or_error if success else None,
            "error": None if success else transaction_id_or_error or "Transaction failed"
        }
        
        print(f"Transaction result: {response_data}")
        
        return Message(
            message_type="PROCESS_TRANSACTION_RESPONSE",
            sender="BANK_SERVER",
            receiver=message.sender,
            data=response_data,
            message_id=message.message_id
        )
    def run_security_audit(self):
        
        print("\nRunning security audit...")
        
        
        
        pins = []
        for uid, user in self.bank_manager.users.items():
            
            
            test_pin = random.randint(1000, 9999)
            pins.append(test_pin)
        
        
        common_pins = [1234, 5678, 9999, 1111, 2222]
        pins.extend(common_pins)
        
        
        demonstrate_pin_vulnerability(pins)

    def handle_get_merchant_info(self, message):
        
        merchant_id = message.data.get("merchant_id")
        
        
        merchant = self.bank_manager.merchants.get(merchant_id)
        
        if merchant:
            response_data = {
                "success": True,
                "merchant_name": merchant.name,
                "bank_code": merchant.bank_code
            }
        else:
            response_data = {
                "success": False,
                "error": "Merchant not found"
            }
        
        return Message(
            message_type="GET_MERCHANT_INFO_RESPONSE",
            sender="BANK_SERVER",
            receiver=message.sender,
            data=response_data,
            message_id=message.message_id
        )

    def handle_verify_pin(self, message):
        
        user_id = message.data.get("user_id")
        pin = message.data.get("pin")
        
        
        user = self.bank_manager.users.get(user_id)
        
        if not user:
            response_data = {
                "success": False,
                "error": "User not found"
            }
        else:
            
            hashed_pin = generate_sha256_hash(pin)
            print(f"Debug - Comparing PINs: User PIN: {user.pin}, Entered PIN (hashed): {hashed_pin}")
            if user.pin == hashed_pin:
                response_data = {
                    "success": True
                }
            else:
                response_data = {
                    "success": False,
                    "error": "Incorrect PIN"
                }
        
        return Message(
            message_type="VERIFY_PIN_RESPONSE",
            sender="BANK_SERVER",
            receiver=message.sender,
            data=response_data,
            message_id=message.message_id
        )

    def verify_blockchain_command(self):
        
        print("\nAvailable Banks:")
        bank_names = set()
        for code, bank in self.bank_manager.banks.items():
            bank_names.add(bank.name)
        
        for i, bank_name in enumerate(sorted(bank_names), 1):
            print(f"  {i}. {bank_name}")
        
        bank_choice = input("\nEnter bank number to verify: ")
        try:
            bank_index = int(bank_choice) - 1
            bank_name = sorted(bank_names)[bank_index]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return
        
        if bank_name not in self.bank_manager.blockchains:
            print(f"No blockchain found for {bank_name}.")
            return
        
        is_valid = self.bank_manager.blockchains[bank_name].is_chain_valid()
        if is_valid:
            print(f"Blockchain for {bank_name} is valid and secure.")
        else:
            print(f"WARNING: Blockchain for {bank_name} has been tampered with!")

    def show_blockchain_command(self):
        
        print("\nAvailable Banks:")
        bank_names = set()
        for code, bank in self.bank_manager.banks.items():
            bank_names.add(bank.name)
        
        for i, bank_name in enumerate(sorted(bank_names), 1):
            print(f"  {i}. {bank_name}")
        
        bank_choice = input("\nEnter bank number to display blockchain: ")
        try:
            bank_index = int(bank_choice) - 1
            bank_name = sorted(bank_names)[bank_index]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return
        
        if bank_name not in self.bank_manager.blockchains:
            print(f"No blockchain found for {bank_name}.")
            return
        
        blockchain = self.bank_manager.blockchains[bank_name]
        print(f"\n==== Blockchain for {bank_name} ====")
        for i, block in enumerate(blockchain.chain):
            if i == 0:
                print(f"Genesis Block:")
            else:
                print(f"Block {i}:")
            print(f"  Transaction ID: {block.transaction_id}")
            print(f"  Timestamp: {time.ctime(block.timestamp)}")
            print(f"  Previous Hash: {block.previous_hash}")
            if i > 0:  
                print(f"  Sender: {block.transaction_data.get('sender_id', 'N/A')}")
                print(f"  Receiver: {block.transaction_data.get('receiver_id', 'N/A')}")
                print(f"  Amount: {block.transaction_data.get('amount', 'N/A')}")
            print()

    def register_bank_command(self):
        
        print("\n==== Register New Bank ====")
        name = input("Enter bank name: ")
        code = input("Enter bank code (11 characters): ")
        branch = input("Enter branch name: ")
        
        success, result = self.bank_manager.register_bank(name, code, branch)
        
        if success:
            print("\n==== Registration Successful ====")
            print(f"Bank Name: {name}")
            print(f"Bank Code: {code}")
            print(f"Branch: {branch}")
            print("================================")
        else:
            print(f"Registration failed: {result}")

    def list_banks(self):
        
        if not self.bank_manager.banks:
            print("No banks registered.")
            return
        
        print("\n==== Registered Banks ====")
        for code, bank in self.bank_manager.banks.items():
            print(f"Bank Code: {code}")
            print(f"Name: {bank.name}")
            print("Branches:")
            for branch in bank.branches:
                print(f"  - {branch}")
            print("------------------------")
        print()


if __name__ == "__main__":
    bank_server = BankServer()
    bank_server.start()
