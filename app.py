import requests
from web3 import Web3, HTTPProvider
import json

def fetch_proxies(proxies_json_url):
    response = requests.get(proxies_json_url)
    response.raise_for_status()
    return response.json()

def test_proxy(proxy):
    proxy_url = proxy['proxy']
    try:
        # Setup web3 with the proxy
        web3 = Web3(HTTPProvider('https://sepolia.infura.io/v3/4e0625c5f11f4c7b97100b9c95984e13', request_kwargs={'proxies': {'http': proxy_url, 'https': proxy_url}}))
        # Call eth_blockNumber method to test the proxy
        block_number = web3.eth.block_number
        print(f"Proxy {proxy_url} works, block number: {block_number}")
        return True
    except Exception as e:
        print(f"Proxy {proxy_url} failed: {e}")
        return False

def main():
    proxies_json_url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json"  # Replace with the actual URL
    proxies = fetch_proxies(proxies_json_url)
    print(proxies) 
    working_proxies = [proxy for proxy in proxies if test_proxy(proxy)]
    
    print("Working proxies:", working_proxies)
    with open('working_proxies.json', 'w') as f:
        json.dump(working_proxies, f, indent=4)

if __name__ == "__main__":
    main()
