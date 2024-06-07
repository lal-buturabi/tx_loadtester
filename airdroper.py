import os


from web3 import Web3
from web3.exceptions import TimeExhausted
from eth_account import Account
from dotenv import load_dotenv
import pickle
load_dotenv()


RPC_URL = os.getenv('RPC_URL')
MAIN_ACC = os.getenv('MAIN_ACC')
AIRDROP_AMT = os.getenv('AIRDROP_AMT')
MAIN_ACC_PVT_KEY = os.getenv('MAIN_ACC_PVT_KEY')

addrList = [
    
]

def createTxn(web3, rcvAddr, i):
    txn = {
        'to': rcvAddr,
        'value': web3.to_wei(AIRDROP_AMT, 'ether'),
        'gas': 21000,
        'gasPrice': (web3.eth.gas_price + 1000 * i),
        'nonce': web3.eth.get_transaction_count(MAIN_ACC),
    }
    return txn

def airdropCoins(addrListArr):
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    sender = Account.from_key(MAIN_ACC_PVT_KEY)
    print('0.001 ETH: ', web3.to_wei('0.001', 'ether'))
    l = len(addrListArr)

    i = 0
    # resume code
    # while True:
    #     if addrListArr[i][0] == '0x086971D902bA94B4083B13cfb1d2281B01f4f58C':
    #         break
    #     i += 1
    while i < l:
        try:
            addr = addrListArr[i][0]
            
            txn = createTxn(web3, addr, i)
            signedTxn = web3.eth.account.sign_transaction(txn, sender.key)
            print('sending amount to ', addr, txn['nonce'], txn['gasPrice'], txn['value'])
            txHash = web3.eth.send_raw_transaction(signedTxn.rawTransaction)
            # print('tx hash: ', txHash)
            # print('waiting for the txn receipt..')
            # time.sleep(1)
            web3.eth.wait_for_transaction_receipt(txHash)
            print('sent.')
            i += 1
        except (ValueError, TimeExhausted) as e:
            continue
    pass

files = [
    'wallets_1800.pkl'
]

def main(): 
    print(f'Fund amount: {AIRDROP_AMT} STC')
    addrListArr = []
    with open(f'{files[0]}', 'rb') as file:
        addrListArr = pickle.load(file)
    print(f'Total address to fund {len(addrListArr)}')
    if len(addrListArr) > 0:
        airdropCoins(addrListArr)
    # web3 = Web3(Web3.HTTPProvider(RPC_URL))
    # print(web3.eth.gas_price)

if __name__ == '__main__':
    main()