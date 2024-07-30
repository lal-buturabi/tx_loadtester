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
AIRDROP_AMT = 0.5

def createTxn(web3, rcvAddr, amt, gas, gp):
    txn = {
        'to': rcvAddr,
        'value': amt,
        'gas': gas,
        'gasPrice': gp,
        'chainId': web3.eth.chain_id,
        'nonce': web3.eth.get_transaction_count(MAIN_ACC),
    }
    return txn

def airdropCoins(addrListArr):
    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    total_accs = 100
    gas_units = 21000
    gprice_per_unit = web3.eth.gas_price
    gas_amt_per_txn = gas_units * gprice_per_unit
    net_gas_amt = total_accs * gas_amt_per_txn
    total_amt = web3.eth.get_balance(MAIN_ACC)
    net_total = total_amt - net_gas_amt
   
    ac = 57000003996000
    tac = ac * total_accs
    b = total_amt + tac
    print(f'tac: {tac} b: {b} ttl: {total_amt}')

    amt_per_txn = net_total // total_accs
    print(f'gp: {gprice_per_unit}\ngapt: {gas_amt_per_txn}\nnetgas: {net_gas_amt}\ntotalAmt: {total_amt}\nnetTotal: {net_total}')
    print('amt_per_txn: ', amt_per_txn, len(str(amt_per_txn)))
    
    sender = Account.from_key(MAIN_ACC_PVT_KEY)
    #print('0.001 ETH: ', web3.to_wei('0.001', 'ether'))
    l = total_accs

    i = 0
    # resume code
    # while True:
    #     if addrListArr[i][0] == '0xb1ebb571231db383B7AC3dc0E8Fd49b48412e58a':
    #         break
    #     i += 1
    while i < l:
        try:
            addr = addrListArr[i][0]
            
            txn = createTxn(web3, addr, amt_per_txn, gas_units, gprice_per_unit)
            print('sending txn: ', txn)
            signedTxn = web3.eth.account.sign_transaction(txn, sender.key)
            # print('sending amount to ', addr, txn['nonce'], txn['gasPrice'], txn['value'])
            txHash = web3.eth.send_raw_transaction(signedTxn.rawTransaction)
            # print('tx hash: ', txHash)
            # print('waiting for the txn receipt..')
            # time.sleep(1)
            web3.eth.wait_for_transaction_receipt(txHash)
            print('sent.')
            i += 1
        except (ValueError, TimeExhausted) as e:
            print('[Err] retrying..', e)
            continue
    pass

files = [
    'wallets_2000.pkl'
]

def main(): 
    #print(f'Fund amount: {AIRDROP_AMT} STC')
    addrListArr = []
    with open(f'{files[0]}', 'rb') as file:
        addrListArr = pickle.load(file)
    # print(f'Total address to fund {len(addrListArr)}')
    if len(addrListArr) > 0:
        airdropCoins(addrListArr)
    # web3 = Web3(Web3.HTTPProvider(RPC_URL))
    # print(web3.eth.gas_price)

if __name__ == '__main__':
    main()
