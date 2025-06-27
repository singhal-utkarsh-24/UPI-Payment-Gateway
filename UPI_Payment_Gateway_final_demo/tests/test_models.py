import sys
import os
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import User, Merchant, Bank, Transaction

class TestModels(unittest.TestCase):
    
    def test_user_creation(self):
        
        user = User(
            uid="12345",
            name="John Doe",
            mmid="1234567",
            pin="hashedpin123",
            account_number="123456789",
            bank_code="SBIN0000001",
            balance=1000.0
        )
        
        self.assertEqual(user.uid, "12345")
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.mmid, "1234567")
        self.assertEqual(user.balance, 1000.0)
    
    def test_transaction_creation(self):
        
        
        transaction = Transaction(
            amount=500.0,
            sender_id="sender123",
            receiver_id="receiver456"
        )
        
        
        self.assertIsNotNone(transaction.id)
        self.assertIsNotNone(transaction.timestamp)
        self.assertEqual(transaction.amount, 500.0)
        self.assertEqual(transaction.sender_id, "sender123")
        self.assertEqual(transaction.receiver_id, "receiver456")
        self.assertEqual(transaction.status, 0)  

if __name__ == "__main__":
    unittest.main()
