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

load_dotenv()

RPC_URL1 = os.getenv('RPC_URL1')
RPC_URL2 = os.getenv('RPC_URL2')
RPC_URL3 = os.getenv('RPC_URL3')
RPC_URL4 = os.getenv('RPC_URL4')
RPC_URL5 = os.getenv('RPC_URL5')
RPC_URL6 = os.getenv('RPC_URL6')
RPC_URL7 = os.getenv('RPC_URL7')
RPC_URL8 = os.getenv('RPC_URL8')

MAIN_ACC = os.getenv('MAIN_ACC')
MAIN_ACC_PVT_KEY = os.getenv('MAIN_ACC_PVT_KEY')

RECVR_ACC = MAIN_ACC
SEND_AMT = os.getenv('SEND_AMT')

rpcs = [
    RPC_URL1,
    RPC_URL2,
    RPC_URL3,
    RPC_URL4,
    RPC_URL5,
    RPC_URL6,
    RPC_URL7,
    RPC_URL8,
]

completed = 0
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

def createTxn(nonce, gp, gas, amt, chid):
    txn = {
        'to': RECVR_ACC,
        'value': amt,
        'gas': gas,
        'gasPrice': gp,
        'nonce': nonce,
        'chainId': chid
    }
    return txn

async def getBal(addr, w):
    bal = 0
    while True:
        await asyncio.sleep(0.1)
        try:
            bal = await w.eth.get_balance(addr)
            break
        except Exception as e:
            continue
    return bal


async def transferCoins(sender, rpc, t, gp, gas, amt, chainId, mini):
    global completed
    addr = sender.address
    web3p = AsyncWeb3(AsyncHTTPProvider(rpc))
    bal = await getBal(addr, web3p)
    
    while bal >= mini:
        await asyncio.sleep(0.1)
        try:
            nonce = await web3p.eth.get_transaction_count(addr)
            txn = createTxn(nonce, gp, gas, amt, chainId)
            signedTxn = web3p.eth.account.sign_transaction(txn, sender.key)
            
            txHash = await web3p.eth.send_raw_transaction(signedTxn.rawTransaction)
            print(f'Sending from {addr} nonce: {nonce} thread #: {t} RPC: {rpc} txHash: {len(txHash)} ..')
            
            # await asyncio.sleep(1)
            await web3p.eth.wait_for_transaction_receipt(txHash, timeout=120)
            print(f'Txn Finalized. Total Accs done: {completed}')
            
            bal = await getBal(addr)
            # await asyncio.sleep(1)
        except (RequestException, Timeout, ProxyError, ConnectionError) as e:
            continue
        except (ValueError, TimeExhausted) as e:
            continue
        except Exception as e:
            continue
    completed += 1
    print(f'bal of {addr} has reached the minimum. \nBal: {bal} Min: {mini} completed: {completed}')

async def transferFromEachWallet(gprice):
    tasks = []
    wallets = []
    with open('wallets_2000.pkl', 'rb') as file:
        wallets = pickle.load(file)

    # this line is to be removed for other cases
    wallets = wallets[:200]
    
    print(f'Total wallets: {len(wallets)}')
    keys  = [w[1] for w in wallets]
    signers = getSigners(keys)
    leng = len(signers)
    each = leng // len(rpcs)
    print(f'num of accs for each thread: {each}')
    signersArr = [
        signers[:each*1],
        signers[each*1:each*2],
        signers[each*2:each*3],
        signers[each*3:each*4],
        signers[each*4:each*5],
        signers[each*5:each*6],
        signers[each*6:each*7],
        signers[each*7:],
    ]
        
    t = 0
    print(f'signers: {leng}')
    print(f'signers: {[len(s) for s in signersArr]}')
    
    chain_id = 9025
    gas_units = 21000
    send_amt = int(SEND_AMT)
    total_amt_per_acc = 498875000000009000

    gas_amt_per_txn = gas_units * gprice
    
    total_amt_per_txn = send_amt + gas_amt_per_txn

    total_txns_per_acc = total_amt_per_acc // total_amt_per_txn
    
    print(f'gp: {gprice}\ngapt: {gas_amt_per_txn}\ntotalAmtPerTxn: {total_amt_per_txn}\ntotalTxnsPerAcc: {total_txns_per_acc}')

    for i, rpc in enumerate(rpcs):
        print(f'RPC: {i}')
        for signer in signersArr[i]:
            await asyncio.sleep(0.001)
            tasks.append(transferCoins(signer, rpc, t, gprice, gas_units, send_amt, chain_id, total_amt_per_txn))
            t += 1
    print(f'Started {len(tasks)} Tasks')
    start = time.time()
    
    await asyncio.gather(*tasks)
    
    total_txns = total_txns_per_acc * leng
    end = time.time()
    total_time = end - start
    print(f'Total time taken: {total_time}')
    tps = total_txns / total_time
    print(f'TPS: {tps}')

async def main():
    global web3
    web3 = None
    web3 = Web3(Web3.HTTPProvider(rpcs[0]))
    
    gprice = web3.eth.gas_price
    
    print(web3.eth.block_number)

    await transferFromEachWallet(gprice)

if __name__ == "__main__":
    asyncio.run(main())

