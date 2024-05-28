import os


from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()


RPC_URL = os.getenv('RPC_URL')
MAIN_ACC = os.getenv('MAIN_ACC')
RECVR_ACC_PVT_KEY = os.getenv('RECVR_ACC_PVT_KEY')
AIRDROP_AMT = os.getenv('AIRDROP_AMT')


def printBalOf(addr, web3):
    print(f'Bal of {addr} = {web3.eth.get_balance(addr)}')


def main():
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    acc = Account.from_key(RECVR_ACC_PVT_KEY)
    printBalOf(acc.address, web3)

if __name__ == '__main__':
    main()