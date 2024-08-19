from tonsdk.contract.wallet import Wallets, WalletVersionEnum


# необходимо в файл wallet.py ввести мнемоническую
# фразу в переменную mnemonic так же в зависимости от
# версии кошелька необходимо поменять параметре
# version=WalletVersionEnum.v4r2, где v4r2 версия
# кошелька на ту которая необходима.

mnemonic = ['secret', 'zoo', 'strike',
            'fluid', 'scheme', 'blame',
            'work', 'fitness', 'roast',
            'scare', 'spring', 'tourist',
            'gesture', 'scheme', 'album',
            'letter', 'flower', 'level',
            'deal', 'seven', 'face',
            'second', 'clog', 'paddle']
mnemonic, pub_k, priv_k, wallet = Wallets.from_mnemonics(mnemonics=mnemonic, version=WalletVersionEnum.v4r2,
                                                         workchain=0)

wallet_addr = wallet.address.to_string(True, True, True)
# print(wallet_addr)
