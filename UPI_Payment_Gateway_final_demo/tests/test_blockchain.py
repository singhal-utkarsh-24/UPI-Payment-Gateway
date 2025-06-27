import sys
import os
import unittest
import time
import json


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bank_server.blockchain import Blockchain, Block, generate_transaction_id

class TestBlockchain(unittest.TestCase):
    
    def test_genesis_block(self):
        
        blockchain = Blockchain()
        self.assertEqual(len(blockchain.chain), 1)
        self.assertEqual(blockchain.chain[0].transaction_id, "0")
        self.assertEqual(blockchain.chain[0].previous_hash, "0")
    
    def test_add_block(self):
        
        blockchain = Blockchain()
        
        
        transaction_data1 = {
            "sender_id": "user1",
            "receiver_id": "merchant1",
            "amount": 100.0,
            "description": "Test payment"
        }
        block1 = blockchain.add_block("tx1", transaction_data1)
        
        
        transaction_data2 = {
            "sender_id": "user2",
            "receiver_id": "merchant2",
            "amount": 200.0,
            "description": "Another payment"
        }
        block2 = blockchain.add_block("tx2", transaction_data2)
        
        
        self.assertEqual(len(blockchain.chain), 3)
        
        
        self.assertEqual(blockchain.chain[1].previous_hash, blockchain.chain[0].hash)
        self.assertEqual(blockchain.chain[2].previous_hash, blockchain.chain[1].hash)
        
        
        self.assertEqual(blockchain.chain[1].transaction_data, transaction_data1)
        self.assertEqual(blockchain.chain[2].transaction_data, transaction_data2)
    
    def test_chain_validation(self):
        
        blockchain = Blockchain()
        
        
        blockchain.add_block("tx1", {"amount": 100})
        blockchain.add_block("tx2", {"amount": 200})
        
        
        self.assertTrue(blockchain.is_chain_valid())
        
        
        blockchain.chain[1].transaction_data["amount"] = 150
        
        
        self.assertFalse(blockchain.is_chain_valid())
    
    def test_transaction_id_generation(self):
        
        uid = "user123"
        mid = "merchant456"
        amount = 100.0
        timestamp = time.time()
        
        tx_id = generate_transaction_id(uid, mid, amount, timestamp)
        
        
        self.assertEqual(len(tx_id), 64)
        
        
        tx_id2 = generate_transaction_id(uid, mid, amount, timestamp)
        self.assertEqual(tx_id, tx_id2)
    
    def test_blockchain_serialization(self):
        
        blockchain = Blockchain()
        blockchain.add_block("tx1", {"amount": 100})
        blockchain.add_block("tx2", {"amount": 200})
        
        
        dict_list = blockchain.to_dict_list()
        
        
        new_blockchain = Blockchain.from_dict_list(dict_list)
