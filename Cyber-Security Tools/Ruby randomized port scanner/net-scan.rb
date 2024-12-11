require 'socket'
require 'timeout'

# Function to generate a random IP address
def generate_random_ip
  Array.new(4) { rand(0..255) }.join('.')
end

# Function to check if port 80 is open on a given IP
def port_open?(ip, port, timeout = 1)
  begin
    Timeout.timeout(timeout) do
      Socket.tcp(ip, port, connect_timeout: timeout).close
      true
    end
  rescue Errno::ECONNREFUSED, Errno::EHOSTUNREACH, Timeout::Error
    false
  end
end

# Scan random IPs for open port 80
def scan_random_ips(count = 10)
  puts "Scanning #{count} random IPs for open port 80..."
  count.times do
    ip = generate_random_ip
    if port_open?(ip, 80)
      puts "[+] Open port 80 found on #{ip}"
    else
      puts "[-] No open port 80 on #{ip}"
    end
  end
end

# Main
if __FILE__ == $0
  puts "Starting Random IP Generator and Port Scanner..."
  print "Enter the number of IPs to scan: "
  ip_count = gets.chomp.to_i
  scan_random_ips(ip_count)
  puts "Scan complete!"
end
