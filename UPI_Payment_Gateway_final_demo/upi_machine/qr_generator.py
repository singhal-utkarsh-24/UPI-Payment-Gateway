
import qrcode
import io
import sys
import os
import json
import base64
import time


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from upi_machine.lwc import generate_vmid, speck_decrypt, get_merchant_from_mapping

def generate_payment_data(merchant_id, amount=None, description=None):
    """
    Generate payment data containing the VMID (Virtual Merchant ID)
    
    Args:
        merchant_id (str): The merchant's unique ID
        amount (float, optional): Pre-filled payment amount
        description (str, optional): Payment description
    
    Returns:
        str: JSON string with payment data
        str: VMID generated for this transaction
    """
    
    timestamp = int(time.time())
    vmid = generate_vmid(merchant_id, timestamp)
    
    
    payment_data = {
        "vmid": vmid,
        "timestamp": str(timestamp)
    }
    
    
    if amount is not None:
        payment_data["amount"] = str(amount)
    if description is not None:
        payment_data["desc"] = description
    
    
    return json.dumps(payment_data), vmid

def decrypt_vmid_to_mid(vmid, timestamp):
    """
    Decrypt Virtual Merchant ID (VMID) back to original Merchant ID (MID)
    
    Args:
        vmid (str): The Virtual Merchant ID to decrypt
        timestamp (int): Timestamp used for encryption
    
    Returns:
        str: Original Merchant ID (MID)
    """
    
    merchant_id = get_merchant_from_mapping(timestamp)
    if merchant_id:
        print(f"Found merchant ID {merchant_id} from saved mapping for timestamp {timestamp}")
        return merchant_id
    
    
    timestamp_str = str(timestamp)
    key = f"UPI{timestamp_str[-8:]}"  
    
    try:
        
        vmid_bytes = bytes.fromhex(vmid)
        
        
        mid_with_timestamp = speck_decrypt(vmid_bytes, key)
        
        
        mid_prefix = mid_with_timestamp[:8]  
        
        
        print(f"Decrypted VMID: {vmid}")
        print(f"Original merchant ID prefix: {mid_prefix}")
        
        
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from bank_server.bank_manager import BankManager
        
        
        bank_manager = BankManager()
        bank_manager.initialize()
        
        
        matching_merchants = []
        for mid in bank_manager.merchants.keys():
            if mid.startswith(mid_prefix[:4]):  
                matching_merchants.append(mid)
        
        if matching_merchants:
            
            mid = matching_merchants[0]
            print(f"Found matching merchant ID: {mid}")
            return mid
        else:
            
            print("No matching merchant found. Registering a test merchant...")
            success, mid = bank_manager.register_merchant(
                name=f"Test Merchant {mid_prefix[:4]}",
                bank_code="SBIN0000001",
                password="password",
                initial_balance=10000.0
            )
            if success:
                print(f"Registered test merchant with ID: {mid}")
                return mid
            else:
                print("Failed to register test merchant")
                return None
    except Exception as e:
        print(f"Error decrypting VMID: {e}")
        return None

def generate_qr_code(data_json):
    """
    Generate QR code from JSON data
    
    Args:
        data_json (str): JSON string to encode in QR
        
    Returns:
        bytes: QR code as PNG image
    """
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data_json)
    qr.make(fit=True)
    
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def save_qr_to_file(qr_data, filename):
    
    with open(filename, 'wb') as f:
        f.write(qr_data)
    return filename

def save_data_to_file(data, filename):
    
    with open(filename, 'w') as f:
        f.write(data)
    return filename
