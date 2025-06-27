import sys
import os
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bank_server.bank_manager import BankManager

class TestBankManager(unittest.TestCase):
    
    def setUp(self):
        
        self.bank_manager = BankManager()
        self.bank_manager.initialize()
    
    def test_user_registration(self):
        
        success, user_id = self.bank_manager.register_user(
            name="Test User",
            bank_code="SBIN0000001",
            account_number="123456789",
            pin="1234"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(user_id)
        self.assertIn(user_id, self.bank_manager.users)
        
        
        user = self.bank_manager.users[user_id]
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.bank_code, "SBIN0000001")
        self.assertEqual(user.account_number, "123456789")
        
        
        self.assertIn(user.mmid, self.bank_manager.mmid_to_uid)
        self.assertEqual(self.bank_manager.mmid_to_uid[user.mmid], user_id)
    
    def test_merchant_registration(self):
        
        success, merchant_id = self.bank_manager.register_merchant(
            name="Test Merchant",
            bank_code="HDFC0000001",
            account_number="987654321"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(merchant_id)
        self.assertIn(merchant_id, self.bank_manager.merchants)
        
        
        merchant = self.bank_manager.merchants[merchant_id]
        self.assertEqual(merchant.name, "Test Merchant")
        self.assertEqual(merchant.bank_code, "HDFC0000001")
        self.assertEqual(merchant.account_number, "987654321")
    
    def test_authentication(self):
        
        
        success, user_id = self.bank_manager.register_user(
            name="Auth Test User",
            bank_code="ICIC0000001",
            account_number="555555555",
            pin="5678"
        )
        
        self.assertTrue(success)
        user = self.bank_manager.users[user_id]
        
        
        auth_success, auth_user = self.bank_manager.authenticate_user(
            mmid=user.mmid,
            pin="5678"
        )
        
        self.assertTrue(auth_success)
        self.assertEqual(auth_user.uid, user_id)
        
        
        auth_fail, _ = self.bank_manager.authenticate_user(
            mmid=user.mmid,
            pin="wrong_pin"
        )
        
        self.assertFalse(auth_fail)
    
    def test_transaction_processing(self):
        
        
        _, sender_id = self.bank_manager.register_user(
            name="Sender User",
            bank_code="SBIN0000001",
            account_number="111111111",
            pin="1111"
        )
        
        _, receiver_id = self.bank_manager.register_merchant(
            name="Receiver Merchant",
            bank_code="HDFC0000001",
            account_number="222222222"
        )
        
        sender = self.bank_manager.users[sender_id]
        receiver = self.bank_manager.merchants[receiver_id]
        
        
        sender_initial_balance = sender.balance
        receiver_initial_balance = receiver.balance
        
        
        transaction_amount = 100.0
        success, transaction_id = self.bank_manager.process_transaction(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=transaction_amount,
            description="Test transaction"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(transaction_id)
        
        
        self.assertEqual(sender.balance, sender_initial_balance - transaction_amount)
        self.assertEqual(receiver.balance, receiver_initial_balance + transaction_amount)
        
        
        self.assertEqual(len(self.bank_manager.transactions), 1)
        transaction = self.bank_manager.transactions[0]
        self.assertEqual(transaction.id, transaction_id)
        self.assertEqual(transaction.sender_id, sender_id)
        self.assertEqual(transaction.receiver_id, receiver_id)
        self.assertEqual(transaction.amount, transaction_amount)

if __name__ == "__main__":
    unittest.main()
