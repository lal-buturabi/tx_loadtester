import json
import threading
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account._utils.mnemonic import Mnemonic

def generate_wallets(num_wallets):
    wallets = []
    mnemonics = Mnemonic('english')
    for _ in range(num_wallets):
        mnemonic = mnemonics.generate()
        account = Account.from_mnemonic(mnemonic)
        wallets.append(account)
    return wallets

def transfer_eth(web3, sender_address, receiver_address, amount):
    txn = {
        'to': receiver_address,
        'value': web3.toWei(amount, 'ether'),
        'gas': 21000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'nonce': web3.eth.getTransactionCount(sender_address),
    }
    signed_txn = web3.eth.account.sign_transaction(txn, sender_address.privateKey.hex())
    return web3.eth.sendRawTransaction(signed_txn.rawTransaction)

def transfer_from_each(wallets, receiver_address, amount):
    threads = []
    for wallet in wallets:
        thread = threading.Thread(target=transfer_eth, args=(web3, wallet.address, receiver_address, amount))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

def main():
    global web3
    web3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/4e0625c5f11f4c7b97100b9c95984e13'))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    wallets = generate_wallets(10)

    for wallet in wallets:
        txn_hash = transfer_eth(web3, '0xYourAddress', wallet.address, 0.1)
        print(f"Transferred 0.1 ETH to {wallet.address}. Txn Hash: {txn_hash.hex()}")

    while True:
        sufficient_balances = True
        for wallet in wallets:
            balance = web3.eth.getBalance(wallet.address)
            if balance < web3.toWei('0.00000000001', 'ether'):
                sufficient_balances = False
                break
        
        if sufficient_balances:
            receiver_address = '0xReceiverAddress'
            amount = 0.00000000001
            transfer_from_each(wallets, receiver_address, amount)
            print("Transferred from each wallet.")
        else:
            print("Not enough balance in all wallets. Waiting for balances to increase.")
            time.sleep(60) 
if __name__ == "__main__":
    main()
