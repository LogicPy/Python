import random
import time
import os
import random
import string
import time

def generate_hex_data(lines=20, values_per_line=8):
    """Generate random hexadecimal data similar to Terminator vision system"""
    hex_data = []
    for _ in range(lines):
        line = []
        for _ in range(values_per_line):
            # Generate random 2-digit hex value
            hex_value = ''.join(random.choice('0123456789ABCDEF') for _ in range(2))
            line.append(hex_value)
        hex_data.append(' '.join(line))
    return hex_data

def generate_binary_data(lines=15, bits_per_line=32):
    """Generate random binary data"""
    binary_data = []
    for _ in range(lines):
        # Generate random binary string
        binary_value = ''.join(random.choice('01') for _ in range(bits_per_line))
        # Format with spaces for readability
        formatted = ' '.join([binary_value[i:i+4] for i in range(0, len(binary_value), 4)])
        binary_data.append(formatted)
    return binary_data

def generate_address_labels(lines=20):
    """Generate memory address labels like 0x0040, 0x0041, etc."""
    addresses = []
    start_addr = 0x0040
    for i in range(lines):
        addr = start_addr + i
        addresses.append(f"0x{addr:04X}")
    return addresses

def generate_terminator_overlay():
    """Generate complete Terminator vision overlay data"""
    print("TERMINATOR VISION SYSTEM")
    print("=" * 40)
    print("MEMORY ADDRESS\tHEX DATA\t\tBINARY DATA")
    print("-" * 60)
    
    addresses = generate_address_labels()
    hex_data = generate_hex_data()
    binary_data = generate_binary_data()
    
    for i in range(len(addresses)):
        print(f"{addresses[i]}\t\t{hex_data[i]}\t{binary_data[i]}")
    
    # Add some random system status
    print("\nSYSTEM STATUS:")
    statuses = [
        "TARGET ACQUISITION: ACTIVE",
        "ENVIRONMENTAL SCAN: 87.3%",
        "THREAT LEVEL: MEDIUM",
        "WEAPON SYSTEMS: ONLINE",
        "VISUAL PROCESSING: 100%",
        "MEMORY USAGE: 72%",
        "PROCESSING POWER: 89%"
    ]
    
    for status in random.sample(statuses, 3):
        print(f"• {status}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_live_terminator_overlay(duration=10):
    """Generate animated Terminator vision overlay"""
    end_time = time.time() + duration
    
    while time.time() < end_time:
        clear_screen()
        print("TERMINATOR VISION SYSTEM - LIVE")
        print("=" * 50)
        
        # Generate slightly different data each frame
        hex_data = generate_hex_data()
        binary_data = generate_binary_data()
        addresses = generate_address_labels()
        
        print("MEMORY ADDRESS\tHEX DATA\t\tBINARY DATA")
        print("-" * 70)
        
        for i in range(min(10, len(addresses))):  # Show fewer lines for animation
            print(f"{addresses[i]}\t\t{hex_data[i]}\t{binary_data[i]}")
        
        # Add some dynamic status
        status_values = [
            f"TARGETS DETECTED: {random.randint(0, 5)}",
            f"SCAN ACCURACY: {random.randint(70, 99)}%",
            f"PROCESSING: {random.choice(['LOW', 'MEDIUM', 'HIGH'])}",
            f"POWER: {random.randint(80, 100)}%"
        ]
        
        print("\nSYSTEM STATUS:")
        for status in status_values:
            print(f"• {status}")
        
        time.sleep(0.5)  # Update every half second

if __name__ == "__main__":
    generate_live_terminator_overlay(1000)  # Run for 10 seconds
