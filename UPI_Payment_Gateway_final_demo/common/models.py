
import datetime
import uuid
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class User:
    uid: str  
    name: str
    mmid: str  
    pin: str  
    account_number: str
    bank_code: str
    mobile_number: str
    password: str  
    balance: float = 0.0

    
@dataclass
class Merchant:
    mid: str  
    name: str
    account_number: str
    bank_code: str
    balance: float = 0.0

@dataclass
class Bank:
    code: str  
    name: str
    branches: List[str]

@dataclass
class Transaction:
    id: str = None
    timestamp: datetime.datetime = None
    amount: float = 0.0
    sender_id: str = None
    receiver_id: str = None
    status: int = 0  
    description: str = ""
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()
