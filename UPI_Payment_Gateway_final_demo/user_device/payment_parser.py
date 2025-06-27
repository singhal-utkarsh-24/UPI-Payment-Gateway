
import json
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def parse_payment_data(payment_data_str):
    """
    Parse payment data containing VMID
    
    Args:
        payment_data_str (str): The payment data JSON string
    
    Returns:
        dict: The payment data with VMID
    """
    try:
        
        payment_data = json.loads(payment_data_str)
        
        
        if "vmid" not in payment_data:
            print("Error: Missing VMID in payment data")
            return None
            
        
        return payment_data
    
    except Exception as e:
        print(f"Error parsing payment data: {e}")
        return None
