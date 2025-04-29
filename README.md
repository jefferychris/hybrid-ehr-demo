# Hybrid EHR Demo

This repository contains a prototype implementation of a hybrid blockchain and IPFS-based architecture for secure, tamper-evident, and low-latency access to electronic health records (EHR).  
It accompanies the UNSW GSOE9011 capstone project report titled:

"A Hybrid Blockchain-IPFS Architecture for Secure and Auditable Medical Data Access"

To reproduce the benchmark, follow these steps:

1. Prerequisites:
   - Python 3.8+
   - Ganache CLI (block interval = 1s)
   - IPFS Daemon (v0.18+)

2. Install dependencies:
   pip install -r requirements.txt

3. Deploy the smart contract and run the simulation:
   python deploy_contract.py
   python simulation_visual.py

4. Generate latency and performance charts:
   python draw_chart.py

Figures and performance results will be generated in the report/figures/ directory and are ready to be included in the final report.

Experimental environment:
- OS: Ubuntu 22.04
- CPU: Intel Core i7-9700 @ 3.00GHz
- RAM: 16 GB
- Tools: Ganache CLI, IPFS Daemon, Python 3.8

License: MIT License  
Feel free to reuse or extend for academic or prototyping purposes.
