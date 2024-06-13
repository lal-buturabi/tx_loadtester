import pickle


wallets = []
with open('wallets_2800.pkl', 'rb') as f:
    wallets = pickle.load(f)
with open('wallets_2000.pkl', 'rb') as f:
    wallets.extend(pickle.load(f))

with open('wallets_4800.pkl', 'wb') as f:
    pickle.dump(wallets, f)
    print('wrote 4800 wallets.')

with open('wallets_4800.pkl', 'rb') as f:
    wallets = pickle.load(f)
    print(len(wallets))
    print(wallets[0])
    print(wallets[-1])