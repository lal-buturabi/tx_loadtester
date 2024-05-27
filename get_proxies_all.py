import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ProxyError, ConnectionError
import json

def fetch_proxies(proxies_json_url):
    response = requests.get(proxies_json_url)
    response.raise_for_status()
    return response.json()['data']

def test_proxy(proxy, op_file):
    protocols = proxy['protocols']
    proxy_url = f"{protocols[0]}://{proxy['ip']}:{proxy['port']}"
    proxies = {}
    for protocol in protocols:
        proxies[protocol] = proxy_url
    adapter = HTTPAdapter(max_retries=1)
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.proxies.update(proxies)
    try:
        response = session.get('https://www.google.com', timeout=5)
        if response.status_code == 200:
            print(f"Proxy {proxy_url} works")
            with open(op_file, 'a') as f:
                json.dump(proxy, f)
                f.write('\n')
            return True
        else:
            print(f"Proxy {proxy_url} returned status code {response.status_code}")
            return False
    except (ProxyError, ConnectionError) as e:
        print(f"Proxy {proxy_url} failed: {e}")
        return False

def main():
    proxies_json_url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"  # Replace with the actual URL
    # proxies_json_url = "https://proxylist.geonode.com/api/proxy-list?protocols=http&speed=medium&limit=500&page=1&sort_by=lastChecked&sort_type=desc"
    proxies = fetch_proxies(proxies_json_url)
    # print(proxies) 
    # for p in proxies:
    #     print(p)
    #     break
    # return
    op_file = 'working_proxies_new.json'
    for proxy in proxies:
        if test_proxy(proxy, op_file):
            print("Proxy added to file:", proxy['ip'])
    

if __name__ == "__main__":
    main()
