from solcx import compile_standard, install_solc
import json
import os

install_solc('0.8.20')  # match your Solidity version

contract_path = os.path.join(os.path.dirname(__file__), "contracts/DocumentVerification.sol")
with open(contract_path, "r") as f:
    source = f.read()

compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"DocumentVerification.sol": {"content": source}},
    "settings": {"outputSelection": {"*": {"*": ["abi","evm.bytecode"]}}}
}, solc_version="0.8.20")

# Save JSON
os.makedirs(os.path.join(os.path.dirname(__file__), "contracts"), exist_ok=True)
json_path = os.path.join(os.path.dirname(__file__), "contracts/DocumentVerification.json")
with open(json_path, "w") as f:
    json.dump(compiled_sol, f, indent=4)

print("✅ Compilation done. JSON at:", json_path)