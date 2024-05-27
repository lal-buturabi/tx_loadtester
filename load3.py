import json
import threading
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account

def load_proxies_from_json(file_path):
    with open(file_path, 'r') as f:
        proxies = json.load(f)
    return proxies

def transfer_eth(web3, sender_private_key, receiver_address, amount):
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

def transfer_from_each(wallets_private_keys, receiver_address, amount, proxies):
    threads = []
    num_proxies = len(proxies)
    for i, private_key in enumerate(wallets_private_keys):
        thread = threading.Thread(target=transfer_eth, args=(web3, private_key, receiver_address, amount))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

def main():
    global web3
    proxies = load_proxies_from_json('proxies.json')
    
    web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    wallets_private_keys = [
        ('0xWalletAddress1', 'private_key1'),
        ('0xWalletAddress2', 'private_key2'),
    ]

    while True:
        receiver_address = '0xReceiverAddress'
        amount = 0.00000000001
        transfer_from_each(wallets_private_keys, receiver_address, amount, proxies)

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

