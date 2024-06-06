import json
import threading
import hashlib
import time
import requests.adapters
from web3 import Web3
from web3.exceptions import TimeExhausted
from eth_account import Account

import os
from dotenv import load_dotenv
import random
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ProxyError, ConnectionError, Timeout, RequestException
from requests.auth import HTTPProxyAuth
# from web3_proxy_providers import HttpWithProxyProvider

load_dotenv()

RPC_URL = os.getenv('RPC_URL')
MAIN_ACC = os.getenv('MAIN_ACC')
SEND_AMT = os.getenv('SEND_AMT')
RECVR_ACC = os.getenv('RECVR_ACC')
MAIN_ACC_PVT_KEY = os.getenv('MAIN_ACC_PVT_KEY')

currProxy = 0
proxiList = []
usedProxies = []
unusedProxies = []
failedProxies = []

pvtKeyList = []

def getSigners():
    return [Account.from_key(key) for key in pvtKeyList]

def parseProxies1(proxies):
    for proxi in proxies:
        p = {}
        p['ip'] = proxi['ip']
        p['port'] = proxi['port']
        p['proto'] = proxi['protocol']
        p['hash'] = hashlib.sha256(f"{ p['ip']}{ p['port']}{ p['proto']}".encode('utf-8')).hexdigest()
        proxiList.append(p)

def parseProxies2(proxies):
    for proxi in proxies:
        for proto in proxi['protocols']:
            p = {}
            p['ip'] = proxi['ip']
            p['port'] = proxi['port']
            p['proto'] = proto
            p['hash'] = hashlib.sha256(f"{ p['ip']}{ p['port']}{ p['proto']}".encode('utf-8')).hexdigest()
            proxiList.append(p)

def handleFailedProxy(proxy):
    releaseProxy(proxy)
    failedProxies.append(proxy)
    return getNextProxy()

def releaseProxy(proxy):
    usedProxies.remove(proxy['hash'])

def getRandomUsedProxy():
    phash = random.choice(usedProxies)
    q = [p for p in proxiList if p['hash'] == phash]
    if len(q) == 0:
        return {}
    return q[0]
def getNextProxy():
    proxy = {}
    for proxi in proxiList:
        phash = proxi['hash']
        if phash in failedProxies or phash in usedProxies:
            continue
        usedProxies.append(phash)
        proxy = proxi
        break
    if proxy == {}:
        proxy = getRandomUsedProxy()
    return proxy

# def getProvider(url):
#     provider = HttpWithProxyProvider(
#         endpoint_uri=RPC_URL,
#         proxy_url=url
#     )
#     return provider

def getProxySession(proxy):
    proxy_url = f"{proxy['proto']}://{proxy['ip']}:{proxy['port']}"
    proxi = {}
    proxi[proxy['proto']] = proxy_url
    adapter = HTTPAdapter(max_retries=1)
    sess = requests.Session()
    sess.mount('http://', adapter)
    sess.mount('https://', adapter)
    sess.proxies.update(proxi)
    sess.proxies = {
        'http': proxy_url,
        'https': proxy_url,
    }
    return (sess, proxy_url)

def loadProxiesFromJsonFile(file_path):
    with open(file_path, 'r') as f:
        proxies = json.load(f)
    return proxies

def createTxn(sendAddr):
    txn = {
        'to': RECVR_ACC,
        'value': web3.to_wei(SEND_AMT, 'ether'),
        'gas': 21000,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(sendAddr),
    }
    return txn

def transferCoins(sender):
    web3p = None
    sess = None
    bal = web3.eth.get_balance(sender.address)
    mini = web3.to_wei(SEND_AMT, 'ether')
    proxy = getNextProxy()
    if proxy != {}:
        sess = getProxySession(proxy)
    while bal > mini:
        txn = createTxn(sender.address)
        signedTxn = web3.eth.account.sign_transaction(txn, sender.key)
        try:
            # web3 with proxy
            # web3p = Web3(provider=getProvider(sess[1]))
            # print(f'Using proxi: {sess[1]} for {sender.address}')
            if proxy == {}:
                web3p = Web3(Web3.HTTPProvider(RPC_URL))
            else:     
                web3p = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={'proxies': {'http': sess[1], 'https': sess[1]}}, session=sess[0]))
            
            txHash = web3p.eth.send_raw_transaction(signedTxn.rawTransaction)
            print(f'sending from {sender.address} ..')
            # time.sleep(1)
            web3p.eth.wait_for_transaction_receipt(txHash)
            print('finalized.')
            # time.sleep(1)
        except (RequestException, Timeout, ProxyError, ConnectionError) as e:
            # print(f"Proxy failed for {sender.address}. trying with next..")
            proxy = handleFailedProxy(proxy)
            sess = getProxySession(proxy)
        except (ValueError, TimeExhausted) as e:
            continue
        except:
            continue
    print(f'bal of {sender.address} has reached the minimum')

def transferFromEachWallet():
    threads = []
    signers = getSigners()
    print(f'signers: {len(signers)}')
    for signer in signers:
        thread = threading.Thread(target=transferCoins, args=(signer,))
        thread.start()
        threads.append(thread)
    print(f'Started {len(threads)} Threads')
    for thread in threads:
        thread.join()

def main():
    global web3
    web3 = None
    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    proxies1 = loadProxiesFromJsonFile('working_proxies.json')
    proxies2 = loadProxiesFromJsonFile('working_proxies_new.json')
    
    parseProxies1(proxies1)
    parseProxies2(proxies2)

    print(f'total proxies: {len(proxiList)}')
    
    transferFromEachWallet()

if __name__ == "__main__":
    main()


