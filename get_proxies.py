import requests
import json

def fetch_proxies(proxies_json_url):
    response = requests.get(proxies_json_url)
    response.raise_for_status()
    return response.json()

def test_proxy(proxy):
    # print("testing: ", proxy)
    proxy_url = f"{proxy['protocols'][0]}://{proxy['ip']}:{proxy['port']}"
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    try:
        response = requests.get('https://www.google.com', proxies=proxies, timeout=10)
        if response.status_code == 200:
            print(f"Proxy {proxy_url} works")
            return True
        else:
            print(f"Proxy {proxy_url} returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Proxy {proxy_url} failed: {e}")
        return False

def main():
    proxies_json_url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"  # Replace with the actual URL
    # proxies_json_url = "https://proxylist.geonode.com/api/proxy-list?protocols=http&speed=medium&limit=500&page=1&sort_by=lastChecked&sort_type=desc"
    proxies = fetch_proxies(proxies_json_url)['data']
    # print(proxies) 
    # for p in proxies:
    #     print(p)
    #     break
    # return
    working_proxies = [proxy for proxy in proxies if test_proxy(proxy)]
    
    print("Working proxies:", working_proxies)
    with open('working_proxies_new.json', 'w') as f:
        json.dump(working_proxies, f, indent=4)

if __name__ == "__main__":
    main()
