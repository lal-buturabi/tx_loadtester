import json
import threading
import time
import requests.adapters
from web3 import Web3
from eth_account import Account

import os
from dotenv import load_dotenv

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ProxyError, ConnectionError
from requests.auth import HTTPProxyAuth

load_dotenv()

RPC_URL = os.getenv('RPC_URL')
MAIN_ACC = os.getenv('MAIN_ACC')
RECVR_ACC = os.getenv('RECVR_ACC')
MAIN_ACC_PVT_KEY = os.getenv('MAIN_ACC_PVT_KEY')

proxiList = []

wallets_private_keys = [
    ('0x4F3e30bA207BD8f226A5676b5bba7cB41279fD35', '0x19ce88a567d07113751f07796498a91806cadad0fcbdd1012a3b3912375fdedf'),
    ('0x66d1F638D2a95CF0587A4B665CE0b612477ea655', '0x86a57b5f472f9f8964b39b95e4441dbadbfbc5f7a54da1d4d0d88d5885db2b3c'),
    ('0xEDdd3d22f257b6c03e5455FEc74A9130ED6EF1C4', '0x995da08d95315cc2dcaa874064a5737fb984a8221ce418e14b54e1e5699aeb0b'),
    ('0x7F428e67eb57ec47D52Dc5A9bb3c7754271E5c13', '0x332341469d2a8e944a3fb977d8719a9c89cfff77ee2b9d1b547b0866324a2cec'),
    ('0xCD0774429Ea88ac38FeD399E56dcE3a7B3E8B261', '0x1e87768ebb5d9b71daa8341ebf22f0e1220a6a704073ea2a3fe5f1bba5930ab9'),
    ('0x0936bb1E3e0ed84FE29be0319d04603F0ED2F5aD', '0x3a28470c72182eac17ba9c6c6e01239264a5c4ea978ebe999f03452c48b724e0'),
    ('0x85CD48BC8204b2e3Dd167db61dB85Eb558548D82', '0xcdf3ed3b63205f56e15c83c2b41df537a460879c67502454abf2effe1206ced7'),
    ('0xB5F2C22dC8967D38b4389543E56dD04FCcA1BB22', '0x80b2d14ee1e6b4cea98f5a6f512a4567422f7f10fca8696cb458844ddc6ef4db'),
    ('0xB5b2F32479B78d08A1ecf4d89bC41B24B699358a', '0xad5e311c676c915e6d9a6fb716fe5c2baf59e27a1ff107e0b014fb5451be4a33'),
    ('0xfdd091ECbaB890Ab9f77c80fE043847599fb53Fe', '0xfdb3b9f0c7b87b77d76143f19bf2d302f3586a5980d326209e58d8ea5d6043c0')
]

def parseProxies1(proxies):
    for proxi in proxies:
        p = {}
        p['ip'] = proxi['ip']
        p['port'] = proxi['port']
        p['proto'] = proxi['protocol']
        proxiList.append(p)

def parseProxies2(proxies):
    for proxi in proxies:
        for proto in proxi['protocols']:
            p = {}
            p['ip'] = proxi['ip']
            p['port'] = proxi['port']
            p['proto'] = proto
            proxiList.append(p)

def getProxySessionFor(proxy):
    proxy_url = f"{proxy['proto']}://{proxy['ip']}:{proxy['port']}"
    proxi = {}
    proxi[proxy['proto']] = proxy_url
    adapter = HTTPAdapter(max_retries=1)
    sess = requests.Session()
    sess.mount('http://', adapter)
    sess.mount('https://', adapter)
    sess.proxies.update(proxi)
    return sess

def loadProxiesFromJsonFile(file_path):
    with open(file_path, 'r') as f:
        proxies = json.load(f)
    return proxies

def transferCoins(web3, sender_private_key, receiver_address, amount):
    sender_address = Account.privateKeyToAccount(sender_private_key).address
    txn = {
        'to': receiver_address,
        'value': web3.toWei(amount, 'ether'),
        'gas': 21000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'nonce': web3.eth.getTransactionCount(sender_address),
    }
    signed_txn = web3.eth.account.sign_transaction(txn, sender_private_key)
    return web3.eth.sendRawTransaction(signed_txn.rawTransaction)

def transferFromEachWallet(pKeys, recvAddr, amt, proxies):
    threads = []
    num_proxies = len(proxies)
    for i, pKey in enumerate(pKeys):
        thread = threading.Thread(target=transferCoins, args=(web3, pKey, recvAddr, amt))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

def main():
    global web3
    proxies1 = loadProxiesFromJsonFile('working_proxies.json')
    proxies2 = loadProxiesFromJsonFile('working_proxies_new.json')

    session = requests.Session()
    web3 = None
    
    
    web3 = Web3(Web3.HTTPProvider(RPC_URL, session=getProxySessionFor(proxiList[0])))

    

    while True:
        rcvAddr = RECVR_ACC
        amount = 0.00000000001
        transferFromEachWallet(wallets_private_keys, rcvAddr, amount, proxies)

        sufficient_balances = True
        for wallet_address, _ in wallets_private_keys:
            balance = web3.eth.getBalance(wallet_address)
            if balance < web3.toWei('0.00000000001', 'ether'):
                sufficient_balances = False
                break
        
        if sufficient_balances:
            print("Balances are sufficient.")
        else:
            print("Not enough balance")
            time.sleep(60)

if __name__ == "__main__":
    main()

