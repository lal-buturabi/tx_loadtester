import json
import threading
import hashlib
import time
import requests.adapters
from web3 import Web3
from web3.exceptions import TimeExhausted
from eth_account import Account

import os
from dotenv import load_dotenv
import random
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ProxyError, ConnectionError, Timeout, RequestException
from requests.auth import HTTPProxyAuth
# from web3_proxy_providers import HttpWithProxyProvider

load_dotenv()

RPC_URL = os.getenv('RPC_URL')
MAIN_ACC = os.getenv('MAIN_ACC')
SEND_AMT = os.getenv('SEND_AMT')
RECVR_ACC = os.getenv('RECVR_ACC')
MAIN_ACC_PVT_KEY = os.getenv('MAIN_ACC_PVT_KEY')

currProxy = 0
proxiList = []
usedProxies = []
unusedProxies = []
failedProxies = []

pvtKeyList = [
    '0x19ce88a567d07113751f07796498a91806cadad0fcbdd1012a3b3912375fdedf',
    '0x86a57b5f472f9f8964b39b95e4441dbadbfbc5f7a54da1d4d0d88d5885db2b3c',
    '0x995da08d95315cc2dcaa874064a5737fb984a8221ce418e14b54e1e5699aeb0b',
    '0x332341469d2a8e944a3fb977d8719a9c89cfff77ee2b9d1b547b0866324a2cec',
    '0x1e87768ebb5d9b71daa8341ebf22f0e1220a6a704073ea2a3fe5f1bba5930ab9',
    '0x3a28470c72182eac17ba9c6c6e01239264a5c4ea978ebe999f03452c48b724e0',
    '0xcdf3ed3b63205f56e15c83c2b41df537a460879c67502454abf2effe1206ced7',
    '0x80b2d14ee1e6b4cea98f5a6f512a4567422f7f10fca8696cb458844ddc6ef4db',
    '0xad5e311c676c915e6d9a6fb716fe5c2baf59e27a1ff107e0b014fb5451be4a33',
    '0xfdb3b9f0c7b87b77d76143f19bf2d302f3586a5980d326209e58d8ea5d6043c0',
    '0x32319e154aa2e25bc68417808654c60b68bfe0a0c70c487e25f4e00ecfa84e8e',
    '0xcad48fcfb248be4f9ce9c35689094f65a844ee7fd1b05d9dad72c57329707df3',
    '0xca0e446b6ce1901fb1aeb7ccf523b706dca69de2248c18f48544c29331a8a70c',
    '0x3bb8c791dbe981e2a9e436bb50aa0cf7c0ee24ec8552315f803fcfb4abaf93a9',
    '0x481f666c6d776872ed948b34e948fbd7ea7402678328d5a070f208bc9ba807ac',
    '0xebee0c86c76f79d38c0ef945443dfd726bff42d6fbdc9375e7bdb47c9240ef22',
    '0xda1fc9c32120527f3c44c8a33ee4733afe761d90cad669a1e3c353587301c509',
    '0x4e98a0e4dfa81851f44da22aa16346021586f3ad37fce769ed06fae02958eff5',
    '0x0e4e68a4339e04667f25f3b21a2cc0c8037b50d8f1a3e7883426e8ef18966e9e',
    '0x3012282b56dfc20ecb0b270f9636788d668f107e64a3041282f372d2a763954e',
    '0xf6f424bc570e5c5be895042edb43d077ec4b90b3c4d2e9eedf7585f22ab899a7',
    '0x138c7c433b461c63cea54b36d80b4791cda71f8d559579b8544859742976305a',
    '0xcd859a3c7a9a1f78cea09b7c44e96f740f39187876ec273d01814184ff195030',
    '0x97afe4b2fc82469dfa9cbdec723c32718d03ceed541a9a3543fc0b264a350a5c',
    '0x46ca7d27d50a0340ce07cfff105f031f52e685fa5900dbd2af00087f2c3a7d91',
    '0x28756e4694c57f96cdf3194da5ac62eaef4f94f0bf3c5b62db00c9bf4e5264df',
    '0xd81c423c012ea0577a380e2cfa884207bd99b24fdf9d35ca46c110ab02d2c3b4',
    '0x0dab9eb14368220c18381504ad8660b3a2a7f38615da998d527a2fffad44a3d7',
    '0x2542c1984659011114c50ac24cf0f456b7918af94d2884e9535bb8d02672898f',
    '0xca0847dad0d75aec3bf081d396ec87993d02d16b35a837aad653a25b32a00f95',
    '0x861c4179662f4c20327a0721bb4f486525857671261fb8da0927d30f272b7bf9',
    '0xe916e242416565e1a9f38879196a9f5f894e1ffc555f18d21c600ef3f12c265a',
    '0x425d3a330f59f5646d9483b5f4bdf44cc9d08c74857641b76082c2305382ddb2',
    '0x8d86e5059ce54e242dc74a66624bb6657ab317a736a6dd808548ff0049571a3d',
    '0x89ae5970f7c38c88303cfd3331c59596b11e519a8b834a991a5237a6a94db3ac',
    '0x6bb6315dd9eefe1e022156ce40582181160fe2bb0720f7e5c75603844de09ad0',
    '0x65732d2c5b24660c89e08821ff8f35202692760f143d205c52613183d866377d',
    '0xe6b8d9bb5e743986eceb95fcdbe44e771a7655f13e179ecf47ee1a87fea09d3c',
    '0xeb02a796a38cc94ec10d2476acc5a8313f3dd2140cbff6216cb6697e69a41044',
    '0xc88efebacbb8d75418c286c0ff7c0d353faeeca4ccddd03b8db1dba1c7ebf993',
    '0x944cf51d1afff1fc9da403e71e2f0b3a73a4292fe4b60c2fd4a113b174941854',
    '0x2357fa0accf8b375ed599ef0f31138eb30ffac8ea632e64682389f1f9cf93bfe',
    '0x8962fd9c9210997b19730119e2c7b5b1e6d2cc15c6c811d8bd98049a738d81bc',
    '0x5de17e6b07203257be0700aa8cd1a752b750390f5ec2cd27a8a80c4e3150f150',
    '0xb536671b4d493f318a98bb0e7dba894d8df8f92c30838f092c945ff891fb7a9a',
    '0x4f0680892024b0516994a3b1809c3ed63307d4a21bc5402eabacdd2773085a33',
    '0x559f8a46329f28f13fabbb84ce015128dc5b1031c250310e10e98f469da59b61',
    '0x3c5d937e474f45e7923316bee08be59ad93d136bcade96a7225fb837fdc33ba7',
    '0x3242f7f171a02810816d35dbd7920f0b11a70272331f20cb6b803a0fded62a9e',
    '0x2439a9c3776b3173f8b4bdac211f1b34cdea42ac6f95077ff9d31254cf3e3b4c',
    '0xa7178cb2bca8af6b6dfe69d4e93fe499d56a69e6d4cf05dcc86e795422595aab',
    '0xda6d106c9b8f3725843e792995d0b2e43d560f149e7e05d218d392e2f7d65ae4',
    '0x6627f04f1dabbfc155c6f1753dac491326c47940d89c72c8409cb5b8f5ae2789',
    '0xfb7aad5f855dd47ad4cfc2ebd19aaae7f3d09a1f015c8c66fa8734377de676d6',
    '0x9d121fcb96fe1db98cfca2fb1e8af0db93b2f88a545eb85ca28a0d9be73db78c',
    '0x26794c4dd30a05a77d2bb3a2cd4817fc358f80d8abb83aeee3a0db0643983d50',
    '0xb804b98d2fe3933bf3ad828a176e74bcf74d5ab2cc2a8ec9cadd383e9f02d490',
    '0xf73ea9645163d34e1d0e4190964e7ccf50095b484926c1c1d26774b7148744a7',
    '0xe5f3b6ea75d7017fe3d10b271afa28b2c0909b4197610a70efaef66edb53ca51',
    '0xde80b41f28c4f65e1019bf09eff634150b797ea6f7921271dd58df36f7d7edc7',
    '0x328afa3418a07fc1419fb142631afa730fe9b4ec23ae6dfb222596d51f593aa6',
    '0x568d2e882161d13d68ae5e80c2539ea6bbdb4fdb7ba45d27b8452c2b2fa6ea3c',
    '0x1f7a9cbb290cefaf1838e82d77ad6cbdccee5bce558ffeb1109da340db019d9d',
    '0x992b217740a6cff8bd60b6a0b40b8d24ab4e997438146ebbe62466f1cce6ca9a',
    '0xa1840b1d8c63de38a93cf7a6333b93a65b0ce5ea2b2914c580ef036a4abb8de2',
    '0x8b87541549dc5984cad988d719fcfcaae140d1117cfe1c12b96efc0f9780744d',
    '0xe211f0f34f40d3fc2d58ac710d3abeb39caf7c9e22e2295282f080b2a4b2353c',
    '0xb35df320f993288652ee8c5907f9e40e825ad0ca4a5ba1ddcf41e0f64497e93b',
    '0x946251aed95417e599ef483b23f524f3f4a8324559b141e986283ab216c890f4',
    '0x37fb496cfec54db34e2098ffe7b6460ea84691d7eee2ab68b53d61c99e534eed',
    '0xa55de43a05c1ba81ce95645084465733606bc4105fa681c6d2a99cbcf628e230',
    '0x61f22bbe8772871d9f551e7a01458fd75e8b38169a6d4dcdc88ec657d2437839',
    '0xa3b6d47fe55fc89028586ebd7caa995beec3d7d2c3d2843461e931914b5b30e4',
    '0xfe918a18d21be7811218fc8c3a1f56055430b0c8830d9141c66412cef9bba4af',
    '0x2815e22a7afa4b119c85c356ea1f88bf4ca7d4901acfb8fa1aea31161c044ebb',
    '0xef106e3991c44ca1ad4fbbc0138ee51199f8320fbf28efd8e75ca5609b0f7284',
    '0x8661a02e0a5be879def02a11906c0495fc86dfe3ddd57ab2afac3f4b4f5191b4',
    '0x6d6e305ec4f58e37869f9d5562ff9bda3858eb8ebd88495ed0604935a5d5d371',
    '0x38907f0520251a5c11874baa0ea6a23093f1dcecc6f619226baee7f8d73f1026',
    '0x5a4c92d29d69968c2fb32cebca775b72bbcf6465868d5cd938924033c9b8fe5d',
    '0xa96f9ca3376438d63745e322be58676ea0c3348211c18687d2987c3b1a88ca89',
    '0x2763045081d72ee8c919d9bd61f82c8749459a2be05e43abbc33ee8a0ca6afd3',
    '0x881197f55dfb3bbd59833500886aa9ea850c028d73a831f963e9364be4aa7523',
    '0x28c97974906a42ecd60d409271365854202ad448e9043b1a24efbc4d4114a540',
    '0xf317f01b48f1d4a3a82ed95a8fc84216181fb44068f6ba7034e57e3b60f5abb3',
    '0x6e8945bfa322ad847a3957cfe27dfb836d5bf01a82a4ab031bc7cd4b33899b28',
    '0x5b2b59f2382712c573ae8ad07d2e1c2d7dfa18963c21167ba5181ca5d87c10d1',
    '0xabe8f99e2fc19d111274a62addc87147f1b067a4ce5c4a29705a2206dec2737a',
    '0x14cb8e247ece7b51a37886c614b63fb487d58062a163a782f9dca27bfc099ced',
    '0x91f78514c300554d4b9d857d67cb93aed125d7e393ae6bea5a0b70de7a08dd36',
    '0x1e53f331359984fa54f10bda1b4fddb05336a36c2e02b0a2ac906cd2c7f8d8fb',
    '0xf9bac1f20dd6b2f08b304e15cdd5244afaa7901aa4aae884f7a65d198f5bc41d',
    '0xd4dc1cd1942e48de20f7d1a0ddcc9be69fb714cad3ead85b5aa90347a3c78066',
    '0x98b6c757c84fab64d0b1e3c064b06eac93f117f35e617dba07fe087a821974fd',
    '0x7e99978af55aa3eadf9a517008c7f81425f66427bcbb76171bea23edb0c09823',
    '0xe0f9705bd3c4a55c40013d80e1541ff6ad0f6a742f5b647f10f42c7cdc8ef3f7',
    '0x545d0619a536286d1c97eb6a337a1c1a421b6367c35226080c782f668922dfb7',
    '0x465ffa002d6b3c659fdac0a5f1c616cb9341b8eb19ff3ec870100294a708f437',
    '0x344824630ca20628b33024b075bfdc15faf6498aee55462d3dea372bad1d22b4',
    '0x6a7867e04279c21113f3134ac635af3d10884f2a933cd95ef1d277b59bdeb5db',
]

def getSigners():
    return [Account.from_key(key) for key in pvtKeyList]

def parseProxies1(proxies):
    for proxi in proxies:
        p = {}
        p['ip'] = proxi['ip']
        p['port'] = proxi['port']
        p['proto'] = proxi['protocol']
        p['hash'] = hashlib.sha256(f"{ p['ip']}{ p['port']}{ p['proto']}".encode('utf-8')).hexdigest()
        proxiList.append(p)

def parseProxies2(proxies):
    for proxi in proxies:
        for proto in proxi['protocols']:
            p = {}
            p['ip'] = proxi['ip']
            p['port'] = proxi['port']
            p['proto'] = proto
            p['hash'] = hashlib.sha256(f"{ p['ip']}{ p['port']}{ p['proto']}".encode('utf-8')).hexdigest()
            proxiList.append(p)

def handleFailedProxy(proxy):
    releaseProxy(proxy)
    failedProxies.append(proxy)
    return getNextProxy()

def releaseProxy(proxy):
    usedProxies.remove(proxy['hash'])

def getRandomUsedProxy():
    phash = random.choice(usedProxies)
    q = [p for p in proxiList if p['hash'] == phash]
    if len(q) == 0:
        return {}
    return q[0]
def getNextProxy():
    proxy = {}
    for proxi in proxiList:
        phash = proxi['hash']
        if phash in failedProxies or phash in usedProxies:
            continue
        usedProxies.append(phash)
        proxy = proxi
        break
    if proxy == {}:
        proxy = getRandomUsedProxy()
    return proxy

# def getProvider(url):
#     provider = HttpWithProxyProvider(
#         endpoint_uri=RPC_URL,
#         proxy_url=url
#     )
#     return provider

def getProxySession(proxy):
    proxy_url = f"{proxy['proto']}://{proxy['ip']}:{proxy['port']}"
    proxi = {}
    proxi[proxy['proto']] = proxy_url
    adapter = HTTPAdapter(max_retries=1)
    sess = requests.Session()
    sess.mount('http://', adapter)
    sess.mount('https://', adapter)
    sess.proxies.update(proxi)
    sess.proxies = {
        'http': proxy_url,
        'https': proxy_url,
    }
    return (sess, proxy_url)

def loadProxiesFromJsonFile(file_path):
    with open(file_path, 'r') as f:
        proxies = json.load(f)
    return proxies

def createTxn(sendAddr):
    txn = {
        'to': RECVR_ACC,
        'value': web3.to_wei(SEND_AMT, 'ether'),
        'gas': 21000,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(sendAddr),
    }
    return txn

def transferCoins(sender):
    web3p = None
    sess = None
    bal = web3.eth.get_balance(sender.address)
    mini = web3.to_wei(SEND_AMT, 'ether')
    proxy = getNextProxy()
    if proxy != {}:
        sess = getProxySession(proxy)
    while bal > mini:
        txn = createTxn(sender.address)
        signedTxn = web3.eth.account.sign_transaction(txn, sender.key)
        try:
            # web3 with proxy
            # web3p = Web3(provider=getProvider(sess[1]))
            # print(f'Using proxi: {sess[1]} for {sender.address}')
            if proxy == {}:
                web3p = Web3(Web3.HTTPProvider(RPC_URL))
            else:     
                web3p = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={'proxies': {'http': sess[1], 'https': sess[1]}}, session=sess[0]))
            
            txHash = web3p.eth.send_raw_transaction(signedTxn.rawTransaction)
            print(f'sending from {sender.address} ..')
            # time.sleep(1)
            web3p.eth.wait_for_transaction_receipt(txHash)
            print('finalized.')
            # time.sleep(1)
        except (RequestException, Timeout, ProxyError, ConnectionError) as e:
            # print(f"Proxy failed for {sender.address}. trying with next..")
            proxy = handleFailedProxy(proxy)
            sess = getProxySession(proxy)
        except (ValueError, TimeExhausted) as e:
            continue
        except:
            continue
    print(f'bal of {sender.address} has reached the minimum')

def transferFromEachWallet():
    threads = []
    signers = getSigners()
    print(f'signers: {len(signers)}')
    for signer in signers:
        thread = threading.Thread(target=transferCoins, args=(signer,))
        thread.start()
        threads.append(thread)
    print(f'Started {len(threads)} Threads')
    for thread in threads:
        thread.join()

def main():
    global web3
    web3 = None
    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    proxies1 = loadProxiesFromJsonFile('working_proxies.json')
    proxies2 = loadProxiesFromJsonFile('working_proxies_new.json')
    
    parseProxies1(proxies1)
    parseProxies2(proxies2)

    print(f'total proxies: {len(proxiList)}')
    
    transferFromEachWallet()

if __name__ == "__main__":
    main()

