import pickle


wallets = []
with open('wallets_4200.pkl', 'rb') as f:
    wallets = pickle.load(f)
    print('1 begin:\t', wallets[0])
    print('1 end:\t', wallets[-1])

with open('wallets_4800.pkl', 'rb') as f:
    tmp = pickle.load(f)
    wallets.extend(tmp)
    print()
    print('2 begin:\t', tmp[0])
    print('2 end:\t', tmp[-1])

with open('wallets_9000.pkl', 'wb') as f:
    pickle.dump(wallets, f)
    print()
    print(f'wrote {len(wallets)} wallets.')

with open('wallets_9000.pkl', 'rb') as f:
    wallets = pickle.load(f)
    print()
    print(f'total wallets so far: {len(wallets)}')
    print('final begin:\t', wallets[0])
    print('final end:\t', wallets[-1])