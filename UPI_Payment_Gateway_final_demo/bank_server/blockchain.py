
import hashlib
import time
import json
from typing import List, Dict, Any, Optional

class Block:
    
    def __init__(self, transaction_id: str, transaction_data: Dict[str, Any], 
                 previous_hash: str, timestamp: Optional[float] = None):
        self.transaction_id = transaction_id  
        self.transaction_data = transaction_data
        self.previous_hash = previous_hash
        self.timestamp = timestamp if timestamp else time.time()
        
        
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "transaction_id": self.transaction_id,
            "transaction_data": self.transaction_data,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, block_dict: Dict[str, Any]) -> 'Block':
        
        return cls(
            transaction_id=block_dict["transaction_id"],
            transaction_data=block_dict["transaction_data"],
            previous_hash=block_dict["previous_hash"],
            timestamp=block_dict["timestamp"]
        )

class Blockchain:
    
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()
        
    def create_genesis_block(self) -> None:
        
        genesis_block = Block(
            transaction_id="0",  
            transaction_data={"message": "Genesis Block"},
            previous_hash="0",
            timestamp=time.time()
        )
        self.chain.append(genesis_block)
        
    def get_latest_block(self) -> Block:
        
        return self.chain[-1]
    
    def add_block(self, transaction_id: str, transaction_data: Dict[str, Any]) -> Block:
        
        previous_block = self.get_latest_block()
        new_block = Block(
            transaction_id=transaction_id,  
            transaction_data=transaction_data,
            previous_hash=previous_block.transaction_id  
        )
        self.chain.append(new_block)
        return new_block
    
    def is_chain_valid(self) -> bool:
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            
            if current_block.previous_hash != previous_block.transaction_id:
                return False
                
        return True
    
    
                
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        
        return [block.to_dict() for block in self.chain]
    
    @classmethod
    def from_dict_list(cls, dict_list: List[Dict[str, Any]]) -> 'Blockchain':
        
        blockchain = cls()
        
        blockchain.chain = []
        
        for block_dict in dict_list:
            blockchain.chain.append(Block.from_dict(block_dict))
            
        return blockchain
    
    def save_to_file(self, filename: str) -> None:
        
        with open(filename, 'w') as file:
            json.dump(self.to_dict_list(), file, indent=4)
    
    @classmethod
    def load_from_file(cls, filename: str) -> Optional['Blockchain']:
        
        try:
            with open(filename, 'r') as file:
                blockchain_data = json.load(file)
                return cls.from_dict_list(blockchain_data)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

def generate_transaction_id(uid: str, mid: str, amount: float, timestamp: float) -> str:
    
    transaction_string = f"{uid}{mid}{amount}{timestamp}".encode()
    return hashlib.sha256(transaction_string).hexdigest()
