import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker for generating fake IP addresses
fake = Faker()

def generate_ip():
    """Generate a random IPv4 address."""
    return fake.ipv4()

def generate_timestamp(start_date, end_date):
    """Generate a random timestamp between start_date and end_date."""
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

def generate_normal_traffic(num_records, start_date, end_date):
    """Generate normal network traffic records."""
    records = []
    for _ in range(num_records):
        source_ip = generate_ip()
        destination_ip = generate_ip()
        bytes_transmitted = int(np.random.normal(loc=5000, scale=1000))  # Average 5000 bytes
        bytes_transmitted = max(bytes_transmitted, 500)  # Ensure bytes > 500
        packets_transmitted = int(np.random.normal(loc=50, scale=10))  # Average 50 packets
        packets_transmitted = max(packets_transmitted, 5)  # Ensure packets > 5
        unique_dest_ips = random.randint(1, 5)  # Between 1 and 5 unique destinations
        total_bytes = bytes_transmitted * unique_dest_ips
        packet_rate = round(np.random.normal(loc=10, scale=2), 2)  # Average 10 packets/sec
        timestamp = generate_timestamp(start_date, end_date)
        is_anomaly = 0  # Normal traffic
        records.append({
            'source_ip': source_ip,
            'destination_ip': destination_ip,
            'bytes': bytes_transmitted,
            'packets': packets_transmitted,
            'unique_dest_ips': unique_dest_ips,
            'total_bytes': total_bytes,
            'packet_rate': packet_rate,
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'is_anomaly': is_anomaly
        })
    return records

def generate_anomalous_traffic(num_records, start_date, end_date):
    """Generate anomalous network traffic records."""
    records = []
    for _ in range(num_records):
        source_ip = generate_ip()
        destination_ip = generate_ip()
        
        # Introduce anomalies in bytes and packets
        # For example, extremely high bytes or packets
        bytes_transmitted = int(np.random.normal(loc=20000, scale=5000))  # Higher average
        bytes_transmitted = max(bytes_transmitted, 10000)  # Ensure bytes > 10,000
        packets_transmitted = int(np.random.normal(loc=200, scale=50))  # Higher average
        packets_transmitted = max(packets_transmitted, 100)  # Ensure packets > 100
        
        unique_dest_ips = random.randint(10, 50)  # Abnormally high number of destinations
        total_bytes = bytes_transmitted * unique_dest_ips
        packet_rate = round(np.random.normal(loc=100, scale=20), 2)  # Extremely high rate
        
        timestamp = generate_timestamp(start_date, end_date)
        is_anomaly = 1  # Anomalous traffic
        records.append({
            'source_ip': source_ip,
            'destination_ip': destination_ip,
            'bytes': bytes_transmitted,
            'packets': packets_transmitted,
            'unique_dest_ips': unique_dest_ips,
            'total_bytes': total_bytes,
            'packet_rate': packet_rate,
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'is_anomaly': is_anomaly
        })
    return records

def create_network_traffic_csv(filename='network_traffic.csv', normal_ratio=0.95, total_records=10000):
    """
    Create a synthetic network traffic CSV file with normal and anomalous records.
    
    Parameters:
    - filename (str): Name of the CSV file to create.
    - normal_ratio (float): Proportion of normal records (between 0 and 1).
    - total_records (int): Total number of records to generate.
    """
    num_normal = int(total_records * normal_ratio)
    num_anomalous = total_records - num_normal
    
    # Define the time range for data generation
    start_date = datetime.now() - timedelta(days=30)  # Last 30 days
    end_date = datetime.now()
    
    print(f"Generating {num_normal} normal traffic records...")
    normal_records = generate_normal_traffic(num_normal, start_date, end_date)
    
    print(f"Generating {num_anomalous} anomalous traffic records...")
    anomalous_records = generate_anomalous_traffic(num_anomalous, start_date, end_date)
    
    # Combine the records
    all_records = normal_records + anomalous_records
    
    # Shuffle the records to mix normal and anomalous traffic
    random.shuffle(all_records)
    
    # Create a DataFrame
    df = pd.DataFrame(all_records)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Dataset saved to {filename} with {len(df)} records.")

if __name__ == "__main__":
    create_network_traffic_csv(filename='network_traffic.csv', normal_ratio=0.95, total_records=10000)
