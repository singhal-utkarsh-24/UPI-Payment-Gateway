
import struct
import time
import os
import json

def rotate_right(val, r_bits, max_bits=32):
    
    return ((val & (2**max_bits-1)) >> r_bits % max_bits) | \
           (val << (max_bits - (r_bits % max_bits)) & (2**max_bits-1))

def rotate_left(val, r_bits, max_bits=32):
    
    return ((val << r_bits % max_bits) & (2**max_bits-1)) | \
           ((val & (2**max_bits-1)) >> (max_bits - (r_bits % max_bits)))

def speck_round(x, y, k):
    
    x = rotate_right(x, 8)
    x = (x + y) & 0xFFFFFFFF
    x = x ^ k
    y = rotate_left(y, 3)
    y = y ^ x
    return x, y

def speck_encrypt(plaintext, key, rounds=10):
    """
    Encrypt using SPECK algorithm (simplified version)
    
    Args:
        plaintext (str): Text to encrypt
        key (str): Encryption key
        rounds (int): Number of rounds
    
    Returns:
        bytes: Encrypted data
    """
    
    plaintext = plaintext.ljust(8, '\0')
    key = key.ljust(8, '\0')
    
    
    x, y = struct.unpack("<II", plaintext[:8].encode())
    
    
    k = struct.unpack("<II", key[:8].encode())[0]
    
    
    for i in range(rounds):
        x = rotate_right(x, 8)
        x = (x + y) & 0xFFFFFFFF
        x = x ^ k
        y = rotate_left(y, 3)
        y = y ^ x
    
    
    return struct.pack("<II", x, y)

def speck_decrypt(ciphertext, key, rounds=10):
    """
    Decrypt using SPECK algorithm (simplified version)
    
    Args:
        ciphertext (bytes): Encrypted data
        key (str): Encryption key
        rounds (int): Number of rounds
    
    Returns:
        str: Decrypted text
    """
    
    x, y = struct.unpack("<II", ciphertext)
    
    
    key = key.ljust(8, '\0')
    k = struct.unpack("<II", key[:8].encode())[0]
    
    
    for i in range(rounds):
        y = y ^ x
        y = rotate_right(y, 3)
        x = x ^ k
        x = (x - y) & 0xFFFFFFFF
        x = rotate_left(x, 8)
    
    
    return struct.pack("<II", x, y).decode().rstrip('\0')

def generate_vmid(mid, timestamp=None):
    """
    Generate Virtual Merchant ID (VMID) using SPECK algorithm
    
    Args:
        mid (str): Merchant ID
        timestamp (int, optional): Timestamp to use, defaults to current time
    
    Returns:
        str: Virtual Merchant ID (VMID)
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    
    
    timestamp_str = str(timestamp)
    key = f"UPI{timestamp_str[-8:]}"  
    
    
    
    input_data = f"{mid[:8]}{timestamp_str[-4:]}"  
    
    print(f"Encrypting merchant ID: {mid}")
    # print(f"Input data for encryption: {input_data}")
    # print(f"Key for encryption: {key}")
    
    
    save_merchant_mapping(mid, timestamp)
    
    
    encrypted = speck_encrypt(input_data, key)
    
    
    vmid = encrypted.hex()
    
    return vmid

def save_merchant_mapping(mid, timestamp):
    
    mapping_file = "merchant_mappings.json"
    mappings = {}
    
    
    try:
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                mappings = json.load(f)
    except Exception as e:
        print(f"Error loading mappings: {e}")
    
    
    timestamp_str = str(timestamp)
    mappings[timestamp_str] = mid
    
    
    try:
        with open(mapping_file, 'w') as f:
            json.dump(mappings, f)
        # print(f"Saved merchant mapping: {timestamp_str} -> {mid}")
    except Exception as e:
        print(f"Error saving mapping: {e}")

def get_merchant_from_mapping(timestamp):
    
    mapping_file = "merchant_mappings.json"
    
    try:
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                mappings = json.load(f)
                
            timestamp_str = str(timestamp)
            if timestamp_str in mappings:
                return mappings[timestamp_str]
    except Exception as e:
        print(f"Error retrieving mapping: {e}")
    
    return None

