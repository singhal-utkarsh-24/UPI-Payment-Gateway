
import math
import random
import time

def gcd(a, b):
    
    while b != 0:
        a, b = b, a % b
    return a

def is_prime(n):
    
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def find_factors(n):
    
    if is_prime(n):
        return [n]

    
    a = random.randint(2, n - 1)

    
    factor = gcd(a, n)
    if factor > 1:
        return [factor, n // factor]

    
    
    
    r = 1
    while pow(a, r, n) != 1:
        r += 1
        
        if r > 1000:
            return [1, n]

    
    if r % 2 == 0:
        x = pow(a, r // 2, n)
        if x != n - 1:
            factor1 = gcd(x - 1, n)
            factor2 = gcd(x + 1, n)
            if factor1 > 1:
                return [factor1, n // factor1]
            if factor2 > 1:
                return [factor2, n // factor2]

    return [1, n]  

def crack_pin(pin, attempts=5):
    
    start_time = time.time()
    
    
    if isinstance(pin, str):
        pin = int(pin)
    
    
    for _ in range(attempts):
        factors = find_factors(pin)
        if len(factors) > 1 and factors != [1, pin]:
            end_time = time.time()
            return {
                "success": True,
                "pin": pin,
                "factors": factors,
                "time_taken": end_time - start_time
            }
    
    end_time = time.time()
    return {
        "success": False,
        "pin": pin,
        "factors": [pin],
        "time_taken": end_time - start_time
    }

def demonstrate_pin_vulnerability(pins=None):
    
    if pins is None:
        pins = [1234, 5678, 9876, 4321]  
    
    print("\n===== QUANTUM VULNERABILITY DEMONSTRATION =====")
    print("Using Shor's Algorithm to demonstrate PIN vulnerabilities")
    print("This simulates how quantum computers could potentially crack PINs")
    print("==================================================\n")
    
    results = []
    for pin in pins:
        result = crack_pin(pin)
        results.append(result)
        
        print(f"Testing PIN: {pin}")
        if result["success"]:
            print(f"  VULNERABLE! PIN {pin} was factored into: {result['factors']}")
            print(f"  Time taken: {result['time_taken']:.4f} seconds")
        else:
            print(f"  PIN {pin} appears resistant to factoring")
            print(f"  Time taken: {result['time_taken']:.4f} seconds")
        print()
    
    
    vulnerable_count = sum(1 for r in results if r["success"])
    print(f"Summary: {vulnerable_count} out of {len(pins)} PINs are vulnerable to quantum attacks")
    print("This demonstrates why quantum-resistant cryptography is important for UPI systems")
    
    return results

if __name__ == "__main__":
    demonstrate_pin_vulnerability()
