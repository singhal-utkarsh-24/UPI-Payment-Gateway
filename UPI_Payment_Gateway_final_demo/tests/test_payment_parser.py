import sys
import os
import unittest
import json
import base64


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_device.payment_parser import parse_payment_data
from upi_machine.qr_generator import generate_payment_data

class TestPaymentParser(unittest.TestCase):
    
    def test_payment_data_parsing(self):
        
        
        merchant_id = "1234567890"
        amount = 100.0
        description = "Test payment"
        
        
        payment_data = generate_payment_data(merchant_id, amount, description)
        
        
        parsed_data = parse_payment_data(payment_data)
        
        
        self.assertIsNotNone(parsed_data)
        self.assertEqual(parsed_data["mid"], merchant_id)
        self.assertEqual(parsed_data["amount"], str(amount))
        self.assertEqual(parsed_data["desc"], description)

if __name__ == "__main__":
    unittest.main()
