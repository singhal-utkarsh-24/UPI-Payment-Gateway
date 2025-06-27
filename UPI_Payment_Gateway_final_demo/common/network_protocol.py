
import json
import base64
from typing import Dict, Any, Union, Optional

class Message:
    
    
    def __init__(self, 
                 message_type: str,
                 sender: str,
                 receiver: str,
                 data: Dict[str, Any],
                 message_id: Optional[str] = None):
        self.message_type = message_type  
        self.sender = sender  
        self.receiver = receiver  
        self.data = data  
        self.message_id = message_id  
    
    def to_json(self) -> str:
        
        
        serializable_data = {}
        for k, v in self.data.items():
            if isinstance(v, bytes):
                serializable_data[k] = base64.b64encode(v).decode('utf-8')
            else:
                serializable_data[k] = v
                
        message_dict = {
            "message_type": self.message_type,
            "sender": self.sender,
            "receiver": self.receiver,
            "data": serializable_data,
            "message_id": self.message_id
        }
        return json.dumps(message_dict)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        
        message_dict = json.loads(json_str)
        return cls(
            message_type=message_dict["message_type"],
            sender=message_dict["sender"],
            receiver=message_dict["receiver"],
            data=message_dict["data"],
            message_id=message_dict["message_id"]
        )
