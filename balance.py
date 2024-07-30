import os
import asyncio
from dotenv import load_dotenv
from web3 import Web3, AsyncWeb3, AsyncHTTPProvider

load_dotenv()

MAIN_ACC = os.getenv('MAIN_ACC')
RPC_URL = os.getenv('RPC_URL')
# addr = '0x3fe80353785E75C14af2dc9566a6bbA5A585FAfF' 
addr = MAIN_ACC 
async def main():
    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    bal = web3.eth.get_balance(addr)
    print(f"balance [{addr}]: ", bal)
    # gp = web3.eth.gas_price
    # print(f"gas price [{MAIN_ACC}]: ", gp)
    # x = 9000 / 
    # total_tokens = web3.to_wei(100, 'ether')
    # num_recipients = 200
    # amt_per_recipient = total_tokens // num_recipients
    # print('Amt: ', amt_per_recipient)
    # gas_price = web3.eth.gas_price
    # print('Gas-price: ', gas_price)
    # gas_per_txn = 21000
    # gas_amt = gas_per_txn * gas_price
    # print('Gas: ', gas_amt)
    # net_amt = amt_per_recipient - gas_amt
    # print('Net Amt: ', net_amt)
    # tx_amt = web3.to_wei(0.5, 'ether')
    # total_txns = net_amt // (tx_amt + gas_amt)
    # print('total txns: ', total_txns)



if __name__ == "__main__":
    asyncio.run(main())

