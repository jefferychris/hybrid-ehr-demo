import json
from web3 import Web3
from solcx import compile_standard, install_solc
from eth_utils import to_checksum_address

# Install specific version of solc (only required once)
install_solc('0.8.0')

# Read the Solidity contract source code
with open("AccessControl.sol", "r") as file:
    source_code = file.read()

# Compile the Solidity contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "AccessControl.sol": {"content": source_code}
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
}, solc_version="0.8.0")

# Extract ABI and bytecode
abi = compiled_sol['contracts']['AccessControl.sol']['AccessControl']['abi']
bytecode = compiled_sol['contracts']['AccessControl.sol']['AccessControl']['evm']['bytecode']['object']

# Connect to local Ganache
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert web3.is_connected(), "Ganache not connected"
account = web3.eth.accounts[0]

# Deploy the contract
AccessControl = web3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = AccessControl.constructor().transact({'from': account})
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress
print(f"[SUCCESS] Contract deployed at: {contract_address}")

# Write ABI and contract address to AccessControl.json
with open("AccessControl.json", "w") as f:
    json.dump({
        "abi": abi,
        "address": contract_address
    }, f, indent=4)

print("[INFO] ABI and address saved to AccessControl.json")
