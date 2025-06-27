import sys
import os
import unittest
import time


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from upi_machine.lwc import speck_encrypt, speck_decrypt, generate_vmid

class TestLWC(unittest.TestCase):
    
    def test_speck_encryption_decryption(self):
        
        plaintext = "test1234"
        key = "secretkey"
        
        
        encrypted = speck_encrypt(plaintext, key)
        self.assertIsNotNone(encrypted)
        
        
        decrypted = speck_decrypt(encrypted, key)
        self.assertEqual(decrypted, plaintext)
    
    def test_vmid_generation(self):
        
        mid = "1234567890abcdef"
        timestamp = int(time.time())
        
        
        vmid = generate_vmid(mid, timestamp)
        self.assertIsNotNone(vmid)
        
        
        self.assertNotEqual(vmid, mid)
        
        
        vmid2 = generate_vmid(mid, timestamp)
        self.assertEqual(vmid, vmid2)
        
        
        vmid3 = generate_vmid(mid, timestamp + 1)
        self.assertNotEqual(vmid, vmid3)

if __name__ == "__main__":
    unittest.main()
