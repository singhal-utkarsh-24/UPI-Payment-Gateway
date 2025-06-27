import sys
import os
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.crypto import generate_sha256_hash, encrypt_data, decrypt_data

class TestCrypto(unittest.TestCase):
    
    def test_sha256_hash(self):
        
        input_str = "1234"
        hash_value = generate_sha256_hash(input_str)
        
        
        self.assertEqual(len(hash_value), 16)
        
        
        self.assertEqual(hash_value, generate_sha256_hash(input_str))
        
        
        self.assertNotEqual(hash_value, generate_sha256_hash("5678"))
    
    def test_encryption_decryption(self):
        
        original_data = "Sensitive payment data"
        
        
        encrypted_data, iv, key, tag = encrypt_data(original_data)
        
        
        self.assertNotEqual(encrypted_data, original_data.encode())
        
        
        decrypted_data = decrypt_data(encrypted_data, iv, key, tag)
        
        
        self.assertEqual(decrypted_data, original_data)

if __name__ == "__main__":
    unittest.main()
