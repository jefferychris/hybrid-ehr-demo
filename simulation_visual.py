import json
import time
import ipfshttpclient
from web3 import Web3
from eth_utils import to_checksum_address
import matplotlib.pyplot as plt
import numpy as np

# ---------- Initialization ----------
ganache_url = "http://127.0.0.1:8545"  # Ganache RPC endpoint
web3 = Web3(Web3.HTTPProvider(ganache_url))
assert web3.is_connected(), "Failed to connect to Ganache"
print("[DEBUG] Connected to Ganache at", ganache_url)

# Load latest contract address and ABI from JSON file
with open("AccessControl.json", "r") as f:
    contract_metadata = json.load(f)
contract_address = to_checksum_address(contract_metadata["address"])
contract = web3.eth.contract(
    address=contract_address,
    abi=contract_metadata["abi"]
)
print(f"[DEBUG] Contract loaded with address: {contract_address}")

# Default accounts
owner_account = web3.eth.accounts[0]
user_account = web3.eth.accounts[1]  # Simulated authorized user
print(f"[DEBUG] Owner account: {owner_account}")
print(f"[DEBUG] Authorized user account: {user_account}")

# ---------- Connect to IPFS ----------
ipfs = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001/http")
print("[DEBUG] Connected to IPFS")

# ---------- Parameters ----------
num_trials = 1000  # Number of test iterations

# ---------- Upload file to IPFS and register on-chain ----------
def upload_and_register(filepath):
    print(f"[INFO] Uploading {filepath} to IPFS...")
    with open(filepath, "rb") as f:
        result = ipfs.add(f)
        ipfs_hash = result["Hash"]
    print(f"[INFO] Uploaded to IPFS: {ipfs_hash}")
    tx_hash = contract.functions.registerFile(ipfs_hash).transact({'from': owner_account})
    web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[INFO] IPFS hash {ipfs_hash} registered on-chain.")
    return ipfs_hash

# ---------- Grant access to a user ----------
def grant_access(user_address):
    tx_hash = contract.functions.grantAccess(user_address).transact({'from': owner_account})
    web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[INFO] Granted access to {user_address}")
    try:
        auth_status = contract.functions.authorized(user_address).call()
        print(f"[DEBUG] Authorized status for {user_address}: {auth_status}")
    except Exception as e:
        print(f"[DEBUG] Could not retrieve authorized status: {e}")

# ---------- Simulate authorized user data access ----------
def access_data(user_address):
    start = time.time()
    try:
        ipfs_hash = contract.functions.accessFile().call({'from': user_address})
        duration = time.time() - start
        print(f"[SUCCESS] User {user_address} accessed data: {ipfs_hash}")
        print(f"[INFO] Access latency: {duration:.4f} seconds")
        print(f"[DEBUG] Latency recorded: {duration:.4f} seconds")
        return ipfs_hash, duration
    except Exception as e:
        print(f"[FAIL] Access denied for {user_address}: {e.args}")
        return None, None

# ---------- Simulate unauthorized access ----------
def unauthorized_access(attacker_address):
    print(f"[TEST] Simulating unauthorized access by {attacker_address}")
    _, _ = access_data(attacker_address)

# ---------- Simulate file tampering and detection ----------
def simulate_tamper_and_detect_record(original_hash, tampered_file_path):
    print("[TEST] Simulating tampered file upload...")
    with open(tampered_file_path, "rb") as f:
        result = ipfs.add(f)
        tampered_hash = result["Hash"]
    print(f"[INFO] Tampered IPFS hash: {tampered_hash}")
    if tampered_hash != original_hash:
        print("[ALERT] Tampering detected: hashes do not match!")
        return True
    else:
        print("[INFO] No tampering detected.")
        return False

# ---------- Save metrics and generate charts ----------
def save_metrics_and_generate_plots(metrics):
    # Save metrics to file
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
    print("[INFO] Metrics saved to metrics.json")

    # Boxplot: latency distribution
    plt.figure(figsize=(8, 6))
    if metrics["authorized_latencies"]:
        plt.boxplot(metrics["authorized_latencies"], patch_artist=True)
    else:
        plt.text(0.5, 0.5, 'No Data', fontsize=12, ha='center')
    plt.title("Authorized Access Latency Distribution")
    plt.ylabel("Latency (seconds)")
    plt.savefig("authorized_latency_boxplot.png")
    plt.close()
    print("[INFO] Box plot saved as authorized_latency_boxplot.png")

    # Histogram: latency frequency + 95th percentile
    if metrics["authorized_latencies"]:
        latencies = np.array(metrics["authorized_latencies"])
        p95 = np.percentile(latencies, 95)
        plt.figure(figsize=(8, 6))
        plt.hist(latencies, bins=20, color="lightblue", edgecolor="black")
        plt.axvline(p95, color="red", linestyle="dashed", linewidth=2, label=f"95th Percentile: {p95:.4f} sec")
        plt.legend()
        plt.title("Authorized Access Latency Histogram")
        plt.xlabel("Latency (seconds)")
        plt.ylabel("Frequency")
        plt.savefig("authorized_latency_histogram.png")
        plt.close()
        print("[INFO] Histogram saved as authorized_latency_histogram.png")
    else:
        print("[INFO] No authorized latency data to generate histogram.")

    # Bar chart: unauthorized access attempts
    plt.figure(figsize=(8, 6))
    categories = ["Unauthorized Attempts", "Blocked Attempts"]
    values = [metrics["unauthorized_attempts"], metrics["blocked_unauthorized_attempts"]]
    plt.bar(categories, values, color=["skyblue", "salmon"], edgecolor="black")
    plt.title("Unauthorized Access Attempts")
    plt.ylabel("Count")
    plt.savefig("unauthorized_access_bar.png")
    plt.close()
    print("[INFO] Bar chart saved as unauthorized_access_bar.png")

    # Bar chart: tamper detection result
    plt.figure(figsize=(8, 6))
    categories = ["Tamper Detection (1=Detected)"]
    values = [1 if metrics["tamper_detection"] else 0]
    plt.bar(categories, values, color=["lightgreen"], edgecolor="black")
    plt.title("Tamper Detection Result")
    plt.ylim(0, 1.5)
    plt.savefig("tamper_detection_bar.png")
    plt.close()
    print("[INFO] Bar chart saved as tamper_detection_bar.png")


if __name__ == "__main__":
    # 1. Upload and register the original file
    original_hash = upload_and_register("origin_data/test_upload_file.txt")

    # 2. Grant access to authorized user
    grant_access(user_account)

    # 3. Simulate multiple authorized accesses and record latencies
    authorized_latencies = []
    for i in range(num_trials):
        print(f"[TEST] Authorized access simulation #{i+1}")
        _, latency = access_data(user_account)
        if latency is not None:
            authorized_latencies.append(latency)
            print(f"[DEBUG] Current authorized_latencies (trial {i+1}): {authorized_latencies}")
    if not authorized_latencies:
        print("[DEBUG] No authorized latency data recorded.")

    # 4. Simulate multiple unauthorized accesses
    unauthorized_attempts = num_trials
    blocked_attempts = 0
    for i in range(num_trials):
        print(f"[TEST] Unauthorized access simulation #{i+1}")
        _, latency = access_data(web3.eth.accounts[2])
        if latency is None:
            blocked_attempts += 1

    # 5. Simulate tampering detection
    tamper_detection_result = simulate_tamper_and_detect_record(original_hash, "/data/9011/changed_data/test_upload_file.txt")

    # 6. Summarize metrics
    metrics = {
        "authorized_latencies": authorized_latencies,
        "average_authorized_latency": sum(authorized_latencies) / len(authorized_latencies) if authorized_latencies else None,
        "unauthorized_attempts": unauthorized_attempts,
        "blocked_unauthorized_attempts": blocked_attempts,
        "tamper_detection": tamper_detection_result
    }

    # Save metrics and generate all plots
    save_metrics_and_generate_plots(metrics)

    print("All metrics and plots generated successfully.")
