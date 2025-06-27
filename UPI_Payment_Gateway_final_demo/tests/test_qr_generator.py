import sys
import os
import unittest
import json
import base64


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from upi_machine.qr_generator import generate_payment_data, generate_qr_code, save_data_to_file, save_qr_to_file

class TestQRGenerator(unittest.TestCase):
    
    def test_payment_data_generation(self):
        
        merchant_id = "1234567890abcdef"
        
        
        payment_data, vmid = generate_payment_data(merchant_id)
        self.assertIsNotNone(payment_data)
        self.assertIsNotNone(vmid)
        
        
        payment_dict = json.loads(payment_data)
        self.assertIn("data", payment_dict)
        self.assertIn("iv", payment_dict)
        self.assertIn("key", payment_dict)
        self.assertIn("tag", payment_dict)
        
        
        payment_data_with_amount, vmid = generate_payment_data(merchant_id, amount=100.0, description="Test payment")
        self.assertIsNotNone(payment_data_with_amount)
        
        
        test_file = "test_payment_data.txt"
        save_data_to_file(payment_data, test_file)
        
        
        self.assertTrue(os.path.exists(test_file))
        
        
        os.remove(test_file)
    
    def test_qr_code_generation(self):
        
        try:
            
            test_data = json.dumps({"test": "data"})
            
            
            qr_data = generate_qr_code(test_data)
            self.assertIsNotNone(qr_data)
            
            
            test_file = "test_qr.png"
            save_qr_to_file(qr_data, test_file)
            
            
            self.assertTrue(os.path.exists(test_file))
            
            
            os.remove(test_file)
        except ImportError:
            self.skipTest("qrcode library not installed")

if __name__ == "__main__":
    unittest.main()
