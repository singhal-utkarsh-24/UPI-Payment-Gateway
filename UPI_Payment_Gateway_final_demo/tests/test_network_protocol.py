import sys
import os
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.network_protocol import Message

class TestNetworkProtocol(unittest.TestCase):
    
    def test_message_serialization(self):
        
        
        original_message = Message(
            message_type="TEST_MESSAGE",
            sender="TEST_SENDER",
            receiver="TEST_RECEIVER",
            data={"key1": "value1", "key2": 123},
            message_id="msg123"
        )
        
        
        json_str = original_message.to_json()
        
        
        reconstructed_message = Message.from_json(json_str)
        
        
        self.assertEqual(reconstructed_message.message_type, original_message.message_type)
        self.assertEqual(reconstructed_message.sender, original_message.sender)
        self.assertEqual(reconstructed_message.receiver, original_message.receiver)
        self.assertEqual(reconstructed_message.message_id, original_message.message_id)
        self.assertEqual(reconstructed_message.data["key1"], original_message.data["key1"])
        self.assertEqual(reconstructed_message.data["key2"], original_message.data["key2"])
    
    def test_binary_data_handling(self):
        
        
        binary_data = b"binary\x00\x01\x02data"
        original_message = Message(
            message_type="BINARY_TEST",
            sender="SENDER",
            receiver="RECEIVER",
            data={"text": "Hello", "binary": binary_data},
            message_id="bin123"
        )
        
        
        json_str = original_message.to_json()
        
        
        reconstructed_message = Message.from_json(json_str)
        
        
        self.assertEqual(reconstructed_message.data["text"], "Hello")
        
        

if __name__ == "__main__":
    unittest.main()
