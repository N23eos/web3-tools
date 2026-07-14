from web3 import Web3
import pandas as pd
import time

# Number of attempts to generate wallets
ATTEMPTS = 30000
# Patterns for filtering
PATTERNS = ["0000", "n23eo", "000"]
# Output file name
OUTPUT_FILE = "filtered_wallets_multiple_patterns.xlsx"

# Initialize Web3 connection
connection = Web3()
connection.eth.account.enable_unaudited_hdwallet_features()

# List to store matching wallets
filtered_wallets = []

# Start timing
start_time = time.time()

for attempt in range(ATTEMPTS):
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

        # Stop if the desired number of wallets is found
        if len(filtered_wallets) >= 10:  # Specify the number of wallets to find
            break

    # Periodically print remaining time
    if attempt % 1000 == 0 and attempt > 0:
        elapsed_time = time.time() - start_time
        estimated_total_time = (elapsed_time / attempt) * ATTEMPTS
        remaining_time = estimated_total_time - elapsed_time
        print(f"Progress: {attempt}/{ATTEMPTS}, Estimated time remaining: {remaining_time:.2f} seconds")

# Save the matching wallets to an Excel file
if filtered_wallets:
    df = pd.DataFrame(filtered_wallets)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Filtered wallets saved to {OUTPUT_FILE}")
else:
    print("No wallets matching the patterns were found.")

# Print total elapsed time
total_time = time.time() - start_time
print(f"Total time elapsed: {total_time:.2f} seconds")
