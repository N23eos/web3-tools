from web3 import Web3
import pandas as pd

# Number of accounts to generate
ACCOUNTS_QUANTITY = 10

# Connect to Web3 instance
connection = Web3()
connection.eth.account.enable_unaudited_hdwallet_features()

# List to hold the wallet data
data = []

# Generate accounts
for number in range(ACCOUNTS_QUANTITY):
    account = connection.eth.account.create_with_mnemonic()
    seed_phrase = account[1]
    address = account[0].address
    private_key = account[0].key.hex()

    print(f'Account {number + 1}\n',
          f'Seed: {seed_phrase}\n',
          f'Public: {address}\n',
          f'Private_key: {private_key}\n',
          '--------------------------')

    # Append account details to the list
    data.append({
        'Seed Phrase': seed_phrase,
        'Address': address,
        'Private Key': private_key
    })

# Save to Excel
filename = "generated_wallets.xlsx"
df = pd.DataFrame(data)
df.to_excel(filename, index=False)

print(f"Wallets successfully saved to {filename}")
