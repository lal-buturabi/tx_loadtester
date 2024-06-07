import pickle


# wallets = []
# with open('wallets_1000.pkl', 'rb') as file:
#     wallets = pickle.load(file)
# with open('wallets_1800.pkl', 'rb') as file:
#     wallets.extend(pickle.load(file))

with open('wallets_2800.pkl', 'rb') as file:
    wallets = pickle.load(file)
    print(len(wallets))
    print(wallets[0])
    print(wallets[-1])