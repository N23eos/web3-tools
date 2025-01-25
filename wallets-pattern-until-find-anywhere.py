from web3 import Web3
import pandas as pd
import time

# Patterns for filtering
PATTERNS = ["0x00000", "0x123456", "0xABCDEF", "0xDEADBEEF", "0xBADDCAFE", "0xFEEDFACE", 
 "0xC0FFEE", "0x8BADF00D", "0xCAFEFEED", "0xBAAAAAAD", "0xFACEB00C", "0xDEFACE", "0xC0DE", "0x00000", "0x11111", "0x22222", "0x33333", "0x44444", "0x55555",]
# Output file name
OUTPUT_FILE = "filtered_wallets_multiple_patterns.xlsx"

# Initialize Web3 connection
connection = Web3()
connection.eth.account.enable_unaudited_hdwallet_features()

# List to store matching wallets
filtered_wallets = []

# Start timing
start_time = time.time()

attempt = 0  # Track the number of attempts
while len(filtered_wallets) < 5:  # Continue until 10 wallets are found
    attempt += 1
    # Generate a wallet with a mnemonic
    account = connection.eth.account.create_with_mnemonic()
    seed_phrase = account[1]
    address = account[0].address
    private_key = account[0].key.hex()

    # Check if the address starts with any of the specified patterns
    if any(address.lower().startswith(pattern) for pattern in PATTERNS):
        print(f"Found wallet {len(filtered_wallets) + 1}: {address}")

        # Add wallet details to the list
        filtered_wallets.append({
            "Seed Phrase": seed_phrase,
            "Address": address,
            "Private Key": private_key
        })

    # Periodically print progress
    if attempt % 1000 == 0:
        elapsed_time = time.time() - start_time
        print(f"Attempts: {attempt}, Wallets found: {len(filtered_wallets)}, Elapsed time: {elapsed_time:.2f} seconds")

# Save the matching wallets to an Excel file
df = pd.DataFrame(filtered_wallets)
df.to_excel(OUTPUT_FILE, index=False)
print(f"Filtered wallets saved to {OUTPUT_FILE}")

# Print total elapsed time
total_time = time.time() - start_time
print(f"Total time elapsed: {total_time:.2f} seconds")
