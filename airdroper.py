import os


from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()


RPC_URL = os.getenv('RPC_URL')
MAIN_ACC = os.getenv('MAIN_ACC')
AIRDROP_AMT = os.getenv('AIRDROP_AMT')
MAIN_ACC_PVT_KEY = os.getenv('MAIN_ACC_PVT_KEY')

addrList = [
    # '0x4F3e30bA207BD8f226A5676b5bba7cB41279fD35',
    # '0x66d1F638D2a95CF0587A4B665CE0b612477ea655',
    # '0xEDdd3d22f257b6c03e5455FEc74A9130ED6EF1C4',
    # '0x7F428e67eb57ec47D52Dc5A9bb3c7754271E5c13',
    # '0xCD0774429Ea88ac38FeD399E56dcE3a7B3E8B261',
    # '0x0936bb1E3e0ed84FE29be0319d04603F0ED2F5aD',
    # '0x85CD48BC8204b2e3Dd167db61dB85Eb558548D82',
    # '0xB5F2C22dC8967D38b4389543E56dD04FCcA1BB22',
    # '0xB5b2F32479B78d08A1ecf4d89bC41B24B699358a',
    # '0xfdd091ECbaB890Ab9f77c80fE043847599fb53Fe',
]

def createTxn(web3, rcvAddr, i):
    txn = {
        'to': rcvAddr,
        'value': web3.to_wei(AIRDROP_AMT, 'ether'),
        'gas': 21000,
        'gasPrice': (web3.eth.gas_price + 10000 * i),
        'nonce': web3.eth.get_transaction_count(MAIN_ACC),
    }
    return txn

def airdropCoins():
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    sender = Account.from_key(MAIN_ACC_PVT_KEY)
    print('0.001 ETH: ', web3.to_wei('0.001', 'ether'))

    for i, addr in enumerate(addrList):
        txn = createTxn(web3, addr, i)
        signedTxn = web3.eth.account.sign_transaction(txn, sender.key)
        print('sending amount to ', addr, txn['nonce'], txn['gasPrice'], txn['value'])
        txHash = web3.eth.send_raw_transaction(signedTxn.rawTransaction)
        print('tx hash: ', txHash)
        print('waiting for the txn receipt..')
        web3.eth.wait_for_transaction_receipt(txHash)
        print('received.')
    pass


def main():  
    airdropCoins()
    # web3 = Web3(Web3.HTTPProvider(RPC_URL))
    # print(web3.eth.gas_price)

if __name__ == '__main__':
    main()