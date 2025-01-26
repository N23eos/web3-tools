from web3 import Web3
import pandas as pd
import time

# Patterns for filtering
PATTERNS = [
    "0x000000", "0x1234567", "0xABCDEF", "0xDEADBEEF", "0xBADDCAFE", "0xFEEDFACE", 
    "0xC0FFEE", "0xCAFEFEED", "0xBAAAAAAD", "0xFACEB00C", "0xDEFACE", 
    "0xC0DE", "0x777777", "0x7777777", "0x333333", "0x0040400", "0x55555",
    "0xAAAAAA", "0xBBBBBB", "0xCCCCCC", "0xDDDDDD", "0xEEEEEE", "0xFFFFFF",
    "0x0000000", "0xDEED", "0xB00B", "0xC0C0C",
    "0xBEEFED", "0xDECAFF", "0xBADBAD", "0xF00D", "0x0BADF00D",
    "0xCAFEBABE", "0x000N23E000E", "0xN23E0",
    "0x123456789",
    "7777777", "0000000", "0xL00K", "0xBAD1DEA", "0x123BEEF",
    "0xC0DE123", "0N23E0", "0x1BADB00B", "0xB16B00B5", "0xDEAD10CC",
    "0xBADCA5E", "0xF00BA11", "0x0N23E0", "0x101010", "0xABC123", "0xDEF456",
    "0xFEEDBEEF", "0xFACEFEED", "0x0n23eo", "0x456654", "0xABCBA1", "0xFEDCBA",
    "0x31415926", "0xB00B135", "0xBEEFBEEF",
]


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
save_interval = 1  # Save every 5 wallets
max_wallets = 20  # Max number of wallets to find

try:
    while len(filtered_wallets) < max_wallets:  # Continue until max_wallets are found
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

            # Save progress after every `save_interval` wallets
            if len(filtered_wallets) % save_interval == 0 or len(filtered_wallets) == max_wallets:
                df = pd.DataFrame(filtered_wallets)
                df.to_excel(OUTPUT_FILE, index=False)
                print(f"Progress saved: {len(filtered_wallets)} wallets written to {OUTPUT_FILE}")

        # Periodically print progress
        if attempt % 1000 == 0:
            elapsed_time = time.time() - start_time
            print(f"Attempts: {attempt}, Wallets found: {len(filtered_wallets)}, Elapsed time: {elapsed_time:.2f} seconds")

except KeyboardInterrupt:
    # Handle interruption and save progress
    print("\nScript interrupted. Saving progress...")
    if filtered_wallets:
        df = pd.DataFrame(filtered_wallets)
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"Progress saved to {OUTPUT_FILE}. Exiting...")
    else:
        print("No wallets found. Exiting without saving.")

# Print total elapsed time
total_time = time.time() - start_time
print(f"Total time elapsed: {total_time:.2f} seconds")
