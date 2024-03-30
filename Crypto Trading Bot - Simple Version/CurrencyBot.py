import ccxt
import time
import argparse
import requests

def fetch_analytics_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.
        
        # Assuming the endpoint returns JSON data
        data = response.json()
        print("Analytics Data:", data)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

# Configure the bot
exchange_id = 'kraken'
api_key = '3z/HvW0TDIKdjzz+uEmogoR7frfwvFiZbX+udV4A2IQCGRLM5V/ztlzy'
secret = 'MQMKXqLAF4JNQ42gRZ08VN8FeYLMapht8p2pmwOzlQZIF24oFLRFlhUGDzjB5hn4Nb0j9eKDnuycj6M/J1koiA=='
symbol = 'BTC/USDT'
#symbol = 'XMR/USDT'  # Example of trading pair for Monero

threshold_buy_price = 10000  # Example threshold
threshold_sell_price = 15000  # Example threshold
trade_amount = '0.01'  # Trade amount in BTC

# Initialize the exchange
exchange = getattr(ccxt, exchange_id)({
    'apiKey': api_key,
    'secret': secret,
})

# Add simulated wallet balances
simulated_wallet = {
    "USDT": 130.82,  # Starting with $1000 USDT
    "BTC": 0.1,    # Starting with 0.1 BTC
}

def simulate_buy_order(symbol, amount, price):
    global simulated_wallet
    cost = amount * price
    if simulated_wallet["USDT"] >= cost:
        simulated_wallet["USDT"] -= cost
        simulated_wallet["BTC"] += amount
        print(f"Simulated buying {amount} {symbol} at {price}, new balance: {simulated_wallet}")
    else:
        print("Not enough USDT to simulate buy order.")

def simulate_sell_order(symbol, amount, price):
    global simulated_wallet
    if simulated_wallet["BTC"] >= amount:
        simulated_wallet["BTC"] -= amount
        simulated_wallet["USDT"] += amount * price
        print(f"Simulated selling {amount} {symbol} at {price}, new balance: {simulated_wallet}")
    else:
        print("Not enough Crypto-Currency to simulate sell order.")

# Replace the real order functions with these simulate functions in your main loop

def place_buy_order(symbol, amount, price):
    print(f"Attempting to place a buy order for {amount} of {symbol} at {price} USDT")
    # Uncomment the line below to enable live trading
    # return exchange.create_limit_buy_order(symbol, amount, price)

def place_sell_order(symbol, amount, price):
    print(f"Attempting to place a sell order for {amount} of {symbol} at {price} USDT")
    # Uncomment the line below to enable live trading
    # return exchange.create_limit_sell_order(symbol, amount, price)


def fetch_price():
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

def create_order(type, price):
    global trade_amount  # This ensures you're using the global variable 'trade_amount'
    print(f"Attempting to {type} {trade_amount} currency at {price} USDT")
    # Simulated order execution
    if type == 'buy':
        simulate_buy_order(symbol, float(trade_amount), price)
    elif type == 'sell':
        simulate_sell_order(symbol, float(trade_amount), price)
    # Uncomment the following lines to enable trading with real orders
    #if type == 'buy':
    #    place_buy_order(symbol, trade_amount, price)
    #elif type == 'sell':
    #    place_sell_order(symbol, trade_amount, price)


def trade_logic():
    current_price = fetch_price()
    print(f"Current price of {symbol} is {current_price} USDT")

    if current_price <= threshold_buy_price:
        create_order('buy', current_price)
    elif current_price >= threshold_sell_price:
        create_order('sell', current_price)

def calculate_sma(prices, period):
    if len(prices) >= period:
        return sum(prices[-period:]) / period
    else:
        return None

# Example usage within your trading logic
short_sma_period = 50
long_sma_period = 100
historical_prices = []  # This should be populated with historical data

short_sma = calculate_sma(historical_prices, short_sma_period)
long_sma = calculate_sma(historical_prices, long_sma_period)

if short_sma and long_sma:  # Ensure both SMAs are calculated
    if short_sma > long_sma:
        # Logic to place a buy order
        # Determine amount and price based on your strategy
        pass
    elif short_sma < long_sma:
        # Logic to place a sell order
        # Determine amount and price based on your strategy
        pass

def start_trade():
    try:
        while True:
            trade_logic()
            time.sleep(10)  # Check every minute
    except KeyboardInterrupt:
        print("Trading stopped.")

def analysis(url):
    fetch_analytics_data(url)

def main():
    # Setup argparse for command line arguments
    parser = argparse.ArgumentParser(description='Crypto Trading Bot CLI')
    parser.add_argument('--fetch-analytics', type=str, help='Fetch analytics data from a specified URL')
    
    # Simulating argparse for interactive mode is not straightforward and not the typical use case
    # Here's a simplified command input approach:
    cmd = input("Enter command: ")
    
    if cmd == "start-trade":
        start_trade()
    elif cmd.startswith("analysis"):
        # This is a simplification and does not fully utilize argparse
        # Extracting URL directly from input for demonstration
        _, url = cmd.split()
        analysis(url)

if __name__ == '__main__':
    main()
