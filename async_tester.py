import json
import asyncio
import pickle
import hashlib
import time
import requests.adapters
from web3 import Web3, AsyncWeb3, AsyncHTTPProvider
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

RPC_URL1 = os.getenv('RPC_URL1')
RPC_URL2 = os.getenv('RPC_URL2')
RPC_URL3 = os.getenv('RPC_URL3')
MAIN_ACC = os.getenv('MAIN_ACC')
SEND_AMT = os.getenv('SEND_AMT')
RECVR_ACC = os.getenv('RECVR_ACC')
MAIN_ACC_PVT_KEY = os.getenv('MAIN_ACC_PVT_KEY')

rpcs = [
    RPC_URL1,
    RPC_URL2,
    RPC_URL3
]

currProxy = 0
proxiList = []
usedProxies = []
unusedProxies = []
failedProxies = []


def getSigners(keys):
    return [Account.from_key(key) for key in keys]

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

def createTxn(v):
    txn = {
        'to': RECVR_ACC,
        'value': v,
        'gas': 21000,
        'gasPrice': '',
        'nonce': 0,
    }
    return txn

async def transferCoins(sender, rpc, t):
    while True:
        await asyncio.sleep(0.1)
        try:
            # print(f'sender: {sender.address} rpc: {rpc}')
            web3p = AsyncWeb3(AsyncHTTPProvider(rpc))
            bal = await web3p.eth.get_balance(sender.address)
            mini = web3p.to_wei(SEND_AMT, 'ether')
            # proxy = getNextProxy()
            # if proxy != {}:     
            #     sess = getProxySession(proxy)
            #     web3p = AsyncWeb3(AsyncHTTPProvider(rpc, request_kwargs={'proxies': {'http': sess[1], 'https': sess[1]}}))
            v = web3p.to_wei(SEND_AMT, 'ether')
            txn = createTxn(v)
            # print(f'RPC connection established. {rpc}')
            break
        except Exception as e:
            # print('Execption: ', e)
            continue
    # i = 4
    while bal > mini:
    # while i > 0:
        await asyncio.sleep(0.1)
        try:
            # print(1)
            txn['gasPrice'] = await web3p.eth.gas_price
            # print('gp', txn['gasPrice'])
            txn['nonce'] = await web3p.eth.get_transaction_count(sender.address)
            # print('nonce', txn['nonce'])
            signedTxn = web3p.eth.account.sign_transaction(txn, sender.key)
            # print('signed')
            # web3 with proxy
            # print(f'Using proxi: {sess[1]} for {sender.address}')
            
            txHash = await web3p.eth.send_raw_transaction(signedTxn.rawTransaction)
            # print('txhash', txHash)
            print(f'sending from {sender.address} thread #: {t} RPC: {rpc} txHash: {len(txHash)} ..')
            # await asyncio.sleep(1)
            await web3p.eth.wait_for_transaction_receipt(txHash)
            print('finalized.')
            # await asyncio.sleep(1)
        except (RequestException, Timeout, ProxyError, ConnectionError) as e:
            # print(f"Proxy failed for {sender.address}. trying with next..")
            # print('Exception: ', e)
            # proxy = handleFailedProxy(proxy)
            # sess = getProxySession(proxy)
            continue
        except (ValueError, TimeExhausted) as e:
            # print('Exception: ', e)
            continue
        except Exception as e:
            # print('Exception: ', e)
            continue
        # i -= 1
    print(f'bal of {sender.address} has reached the minimum')

async def transferFromEachWallet():
    tasks = []
    wallets = []
    with open('wallets_2800.pkl', 'rb') as file:
        wallets = pickle.load(file)
    keys  = [w[1] for w in wallets]
    signers = getSigners(keys)
    leng = len(signers)
    each = leng // len(rpcs)
    signersArr = [
        signers[:each],
        signers[each:each*2],
        signers[each*2:]
    ]
    t = 0
    print(f'signers: {leng}')
    print(f'signers: {[len(s) for s in signersArr]}')
    
    for i, rpc in enumerate(rpcs):
        print(f'RPC: {i}')
        for signer in signersArr[i]:
            await asyncio.sleep(0.001)
            tasks.append(transferCoins(signer, rpc, t,))
            t += 1
    print(f'Started {len(tasks)} Tasks')
    await asyncio.gather(*tasks)

async def main():
    global web3
    web3 = None
    web3 = Web3(Web3.HTTPProvider(rpcs[0]))
    print(web3.eth.block_number)
    # return
    # proxies1 = loadProxiesFromJsonFile('working_proxies.json')
    # proxies2 = loadProxiesFromJsonFile('working_proxies_new.json')
    
    # parseProxies1(proxies1)
    # parseProxies2(proxies2)

    # print(f'total proxies: {len(proxiList)}')
    
    await transferFromEachWallet()

if __name__ == "__main__":
    asyncio.run(main())

