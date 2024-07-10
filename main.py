import time
import random
from web3 import Web3
from eth_account import Account

abi = [
    {
        "inputs": [],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract_address = '0xF502AA456C4ACe0D77d55Ad86436F84b088486F1'

w3 = Web3(Web3.HTTPProvider('https://rpc.linea.build'))

value = Web3.to_wei(0, 'ether')

def get_random_gas_limit(min_gas, max_gas):
    return random.randint(min_gas, max_gas)

def read_private_keys(filename):
    with open(filename, 'r') as file:
        private_keys = file.readlines()
    return [key.strip() for key in private_keys]


private_keys = read_private_keys('private_keys.txt')

random.shuffle(private_keys)

contract = w3.eth.contract(address=contract_address, abi=abi)

successful_accounts = []
failed_accounts = []

for private_key in private_keys:
    try:
        account = Account.from_key(private_key)
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.mint().build_transaction({
            'chainId': 59144,
            'gas': get_random_gas_limit(200000, 300000),
            'gasPrice': w3.eth.gas_price,
            'value': value,
            'nonce': nonce,
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"Транзакция отправлена. Hash: {tx_hash.hex()}")
        
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        if receipt.status == 1:
            print(f"Транзакция от аккаунта {account.address} успешно подтверждена. Hash: {tx_hash.hex()}")
            successful_accounts.append(account.address)
        else:
            print(f"Транзакция от аккаунта {account.address} не удалась. Hash: {tx_hash.hex()}")
            failed_accounts.append(account.address)

    except Exception as e:
        print(f"Ошибка при обработке аккаунта {account.address}: {str(e)}")
        failed_accounts.append(account.address)
    
    random_delay = random.uniform(350, 500)
    rounded_delay = round(random_delay)
    print(f"Ожидаю {rounded_delay} сек. перед следующим аккаунтом")
    time.sleep(rounded_delay)

# Запись успешных аккаунтов в файл
with open('successful.txt', 'w') as file:
    for account_address in successful_accounts:
        file.write(f"{account_address}\n")

# Запись неудачных аккаунтов в файл
with open('failed.txt', 'w') as file:
    for account_address in failed_accounts:
        file.write(f"{account_address}\n")
