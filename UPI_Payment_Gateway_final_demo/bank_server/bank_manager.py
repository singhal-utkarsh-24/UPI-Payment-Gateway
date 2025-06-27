import sys
import os
import uuid
import random
import string
from typing import Dict, Tuple, List, Optional, Any
import time

from bank_server.blockchain import Blockchain, generate_transaction_id
import os
import json



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import User, Merchant, Transaction, Bank
from common.constants import BANK_CODES, PIN_LENGTH, MMID_LENGTH, MID_LENGTH
from common.crypto import generate_sha256_hash

class BankManager:
    def __init__(self):
        self.users: Dict[str, User] = {}  
        self.merchants: Dict[str, Merchant] = {}  
        self.mmid_to_uid: Dict[str, str] = {}  
        self.banks: Dict[str, Bank] = {}  
        self.transactions: Dict[str, Dict[str, Any]] = {}
        self.blockchains: Dict[str, Blockchain] = {}  
        
        
        self.merchants_file = "merchants.json"
        self.users_file = "users.json"

    def initialize(self):
        
        
        banks_data = [
            {
                "name": "State Bank of India",
                "codes": ["SBIN0000001", "SBIN0000002", "SBIN0000003"],
                "branches": ["Main Branch", "City Branch", "Metro Branch"]
            },
            {
                "name": "HDFC Bank",
                "codes": ["HDFC0000001", "HDFC0000002", "HDFC0000003"],
                "branches": ["Main Branch", "City Branch", "Metro Branch"]
            },
            {
                "name": "ICICI Bank",
                "codes": ["ICIC0000001", "ICIC0000002", "ICIC0000003"],
                "branches": ["Main Branch", "City Branch", "Metro Branch"]
            }
        ]
        
        
        self.branch_to_bank = {}
        
        
        blockchain_dir = "blockchain_data"
        if not os.path.exists(blockchain_dir):
            os.makedirs(blockchain_dir)
        
        
        bank_names = ["State Bank of India", "HDFC Bank", "ICICI Bank"]
        for bank_name in bank_names:
            blockchain_file = os.path.join(blockchain_dir, f"blockchain_{bank_name.replace(' ', '_')}.json")
            try:
                if os.path.exists(blockchain_file):
                    self.blockchains[bank_name] = Blockchain.load_from_file(blockchain_file)
                else:
                    self.blockchains[bank_name] = Blockchain()
                    
                    self.blockchains[bank_name].save_to_file(blockchain_file)
            except Exception as e:
                print(f"Error initializing blockchain for {bank_name}: {e}")
                
                self.blockchains[bank_name] = Blockchain()
        
        for bank_data in banks_data:
            bank_name = bank_data["name"]
            for i in range(3):  
                code = bank_data["codes"][i]
                self.banks[code] = Bank(
                    code=code,
                    name=bank_name,
                    branches=[bank_data["branches"][i]]
                )
                
                self.branch_to_bank[code] = bank_name
        
        
        self.load_merchants()
        self.load_users()

    def load_banks(self):
        
        banks_file = "banks.json"
        if os.path.exists(banks_file):
            try:
                with open(banks_file, 'r') as f:
                    banks_data = json.load(f)
                
                for code, bank_data in banks_data.items():
                    self.banks[code] = Bank(
                        code=code,
                        name=bank_data.get('name', ''),
                        branches=bank_data.get('branches', [])
                    )
                    
                    self.branch_to_bank[code] = bank_data.get('name', '')
                print(f"Loaded {len(self.banks)} banks from file")
            except Exception as e:
                print(f"Error loading banks from file: {e}")
                
                self.save_banks()
    
    def save_banks(self):
        
        banks_data = {}
        for code, bank in self.banks.items():
            banks_data[code] = {
                'name': bank.name,
                'branches': bank.branches
            }
        
        try:
            with open("banks.json", 'w') as f:
                json.dump(banks_data, f, indent=2)
            print(f"Saved {len(banks_data)} banks to file")
        except Exception as e:
            print(f"Error saving banks to file: {e}")

    def load_merchants(self):
        
        if os.path.exists(self.merchants_file):
            try:
                with open(self.merchants_file, 'r') as f:
                    merchants_data = json.load(f)
                
                for mid, merchant_data in merchants_data.items():
                    self.merchants[mid] = Merchant(
                        mid=mid,
                        name=merchant_data.get('name', ''),
                        account_number=merchant_data.get('account_number', ''),
                        bank_code=merchant_data.get('bank_code', ''),
                        balance=float(merchant_data.get('balance', 0.0))
                    )
                print(f"Loaded {len(self.merchants)} merchants from file")
            except Exception as e:
                print(f"Error loading merchants from file: {e}")
                
                self.save_merchants()
    
    def save_merchants(self):
        
        merchants_data = {}
        for mid, merchant in self.merchants.items():
            merchants_data[mid] = {
                'name': merchant.name,
                'account_number': merchant.account_number,
                'bank_code': merchant.bank_code,
                'balance': merchant.balance
            }
        
        try:
            with open(self.merchants_file, 'w') as f:
                json.dump(merchants_data, f, indent=2)
            print(f"Saved {len(merchants_data)} merchants to file")
        except Exception as e:
            print(f"Error saving merchants to file: {e}")
    
    def load_users(self):
        
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                
                for uid, user_data in users_data.items():
                    self.users[uid] = User(
                        uid=uid,
                        name=user_data.get('name', ''),
                        mmid=user_data.get('mmid', ''),
                        pin=user_data.get('pin', ''),
                        account_number=user_data.get('account_number', ''),
                        bank_code=user_data.get('bank_code', ''),
                        mobile_number=user_data.get('mobile_number', ''),
                        password=user_data.get('password', ''),
                        balance=float(user_data.get('balance', 0.0))
                    )
                    
                    mmid = user_data.get('mmid', '')
                    if mmid:
                        self.mmid_to_uid[mmid] = uid
                print(f"Loaded {len(self.users)} users from file")
            except Exception as e:
                print(f"Error loading users from file: {e}")
                
                self.save_users()
    
    def save_users(self):
        
        users_data = {}
        for uid, user in self.users.items():
            users_data[uid] = {
                'name': user.name,
                'mmid': user.mmid,
                'pin': user.pin,
                'account_number': user.account_number,
                'bank_code': user.bank_code,
                'mobile_number': user.mobile_number,
                'password': user.password,
                'balance': user.balance
            }
        
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
            print(f"Saved {len(users_data)} users to file")
        except Exception as e:
            print(f"Error saving users to file: {e}")

    def register_user(self, name: str, bank_code: str, mobile_number: str, password: str, pin: str, initial_balance: float = 0.0) -> Tuple[bool, Optional[str]]:
            
            
            if bank_code not in self.banks:
                return False, None
            
            
            import time
            timestamp = str(int(time.time()))
            hash_input = f"{name}{timestamp}{password}"
            uid = generate_sha256_hash(hash_input)  
            
            
            mmid_input = f"{uid}{mobile_number}"
            mmid_hash = generate_sha256_hash(mmid_input)
            
            
            mmid = mmid_hash
            
            
            hashed_pin = generate_sha256_hash(pin)
            
            
            hashed_password = generate_sha256_hash(password)
            
            
            user = User(
                uid=uid,
                name=name,
                mmid=mmid,
                pin=hashed_pin,
                account_number=uid,  
                bank_code=bank_code,
                mobile_number=mobile_number,
                password=hashed_password,  
                balance=initial_balance
            )
            
            
            self.users[uid] = user
            self.mmid_to_uid[mmid] = uid
            
            
            self.save_users()
            
            print(f"Registered user: {name} with MMID: {mmid}")
            return True, uid

    def register_merchant(self, name: str, bank_code: str, password: str, initial_balance: float = 0.0):
        
        
        if bank_code not in self.banks:
            return False, None
        
        
        import time
        timestamp = str(int(time.time()))
        hash_input = f"{name}{timestamp}{password}"
        mid = generate_sha256_hash(hash_input)  
        
        
        merchant = Merchant(
            mid=mid,
            name=name,
            account_number=mid,
            bank_code=bank_code,
            balance=initial_balance
        )
        
        
        self.merchants[mid] = merchant
        
        
        self.save_merchants()
        
        print(f"Registered merchant: {name} with MID: {mid}")
        return True, mid

    
    def authenticate_user(self, mmid: str, password: str) -> Tuple[bool, Optional[User]]:
        
        
        if mmid not in self.mmid_to_uid:
            return False, None
        
        uid = self.mmid_to_uid[mmid]
        user = self.users[uid]
        
        
        hashed_password = generate_sha256_hash(password)
        if user.password != hashed_password:
            return False, None
        
        return True, user

    def process_transaction(self, sender_id: str, receiver_id: str, amount: float, description: str = "") -> Tuple[bool, Optional[str]]:
        
        
        if sender_id not in self.users:
            print(f"Error: Sender ID {sender_id} not found in users database")
            return False, "Sender not found"
        
        
        self.load_merchants()
        
        if receiver_id not in self.merchants:
            print(f"Error: Receiver ID {receiver_id} not found in merchants database")
            print(f"Available merchant IDs: {list(self.merchants.keys())[:5]}...")
            
            
            print(f"Auto-registering merchant with ID: {receiver_id}")
            merchant = Merchant(
                mid=receiver_id,
                name=f"Auto-registered Merchant {receiver_id[:6]}",
                account_number=receiver_id,
                bank_code="SBIN0000001",
                balance=0.0
            )
            self.merchants[receiver_id] = merchant
            self.save_merchants()
        
        sender = self.users[sender_id]
        receiver = self.merchants[receiver_id]
        
        
        if sender.balance < amount:
            print(f"Error: Insufficient balance. User has {sender.balance}, tried to send {amount}")
            return False, "Insufficient balance"
        if amount < 0:
            print("Error: Amount cannot be negative")
            return False, "Invalid amount"
        
        
        timestamp = time.time()
        transaction_id = generate_transaction_id(sender_id, receiver_id, amount, timestamp)
        
        
        sender.balance -= amount
        receiver.balance += amount
        
        
        self.save_users()
        self.save_merchants()
        
        
        transaction = {
            "transaction_id": transaction_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount,
            "description": description,
            "timestamp": timestamp
        }
        self.transactions[transaction_id] = transaction
        
        
        sender_bank = self.branch_to_bank.get(sender.bank_code, "State Bank of India")
        receiver_bank = self.branch_to_bank.get(receiver.bank_code, "State Bank of India")
        
        
        try:
            
            if sender_bank in self.blockchains:
                if self.blockchains[sender_bank] is None:
                    print(f"Creating new blockchain for {sender_bank}")
                    self.blockchains[sender_bank] = Blockchain()
                
                self.blockchains[sender_bank].add_block(
                    transaction_id=transaction_id,
                    transaction_data=transaction
                )
                
                self.blockchains[sender_bank].save_to_file(f"blockchain_{sender_bank.replace(' ', '_')}.json")
            else:
                print(f"Creating new blockchain for {sender_bank}")
                self.blockchains[sender_bank] = Blockchain()
                self.blockchains[sender_bank].add_block(
                    transaction_id=transaction_id,
                    transaction_data=transaction
                )
                self.blockchains[sender_bank].save_to_file(f"blockchain_{sender_bank.replace(' ', '_')}.json")
            
            
            if receiver_bank != sender_bank:
                if receiver_bank in self.blockchains:
                    if self.blockchains[receiver_bank] is None:
                        print(f"Creating new blockchain for {receiver_bank}")
                        self.blockchains[receiver_bank] = Blockchain()
                    
                    self.blockchains[receiver_bank].add_block(
                        transaction_id=transaction_id,
                        transaction_data=transaction
                    )
                    
                    self.blockchains[receiver_bank].save_to_file(f"blockchain_{receiver_bank.replace(' ', '_')}.json")
                else:
                    print(f"Creating new blockchain for {receiver_bank}")
                    self.blockchains[receiver_bank] = Blockchain()
                    self.blockchains[receiver_bank].add_block(
                        transaction_id=transaction_id,
                        transaction_data=transaction
                    )
                    self.blockchains[receiver_bank].save_to_file(f"blockchain_{receiver_bank.replace(' ', '_')}.json")
        
        except Exception as e:
            print(f"Blockchain error: {e}")
            
            
            
        print(f"Processed transaction: {transaction_id} for {amount}")
        return True, transaction_id

    
    def _generate_unique_mmid(self) -> str:
        
        while True:
            mmid = ''.join(random.choices(string.digits, k=MMID_LENGTH))
            if mmid not in self.mmid_to_uid:
                return mmid
    
    def _generate_unique_mid(self) -> str:
        
        while True:
            mid = ''.join(random.choices(string.digits, k=MID_LENGTH))
            if mid not in self.merchants:
                return mid
            
    def verify_blockchain_integrity(self, bank_code: str) -> bool:
        
        if bank_code not in self.blockchains:
            return False
        
        return self.blockchains[bank_code].is_chain_valid()

    def get_transaction_from_blockchain(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        
        
        for bank_code, blockchain in self.blockchains.items():
            for block in blockchain.chain:
                if block.transaction_id == transaction_id:
                    return block.transaction_data
        
        return None

    def get_user_transactions(self, user_id: str) -> List[Dict[str, Any]]:
        
        transactions = []
        
        
        if user_id not in self.users:
            return transactions
        
        bank_code = self.users[user_id].bank_code
        bank_name = self.branch_to_bank[bank_code]
        
        
        if bank_name in self.blockchains:
            blockchain = self.blockchains[bank_name]
            for block in blockchain.chain:
                if block.transaction_id == "0":  
                    continue
                
                transaction_data = block.transaction_data
                if transaction_data.get("sender_id") == user_id or transaction_data.get("receiver_id") == user_id:
                    transactions.append(transaction_data)
        
        return transactions

    def register_bank(self, name: str, code: str, branch: str) -> Tuple[bool, Optional[str]]:
        
        
        if len(code) != 11:
            return False, "Bank code must be 11 characters long"
        
        
        if code in self.banks:
            return False, "Bank code already exists"
        
        
        bank = Bank(
            code=code,
            name=name,
            branches=[branch]
        )
        
        
        self.banks[code] = bank
        self.branch_to_bank[code] = name
        
        
        self.save_banks()
        
        print(f"Registered bank: {name} with code: {code}")
        return True, code


