import sys
from pprint import pprint as pretty
from eth_account import Account
from eth_account.hdaccount import generate_mnemonic#, mnemonic_to_private_key

def generate_wallets(num_wallets):
    Account.enable_unaudited_hdwallet_features()
    wallets = []
    # mnemonics = Mnemonic('english')
    for _ in range(num_wallets):
        mnemonic = generate_mnemonic(num_words=12, lang='english')
        account = Account.from_mnemonic(mnemonic)
        wallets.append(account)
    return wallets


def main():
    N = 500
    if len(sys.argv) > 1:
        N = sys.argv[1]
    
    wallets = [(w.address, w.key.hex()) for w in generate_wallets(N)]
    pretty(wallets)

if __name__ == '__main__':
    main()