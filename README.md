# Narok • Multi-Strategy (Ape + Python)

Vault ERC-4626 com AUM 1%/ano, saída 2% (1% devs / 1% sustain),
3 estratégias (25% cada) + 25% caixa e rebalance via `poke()` (keeper-friendly).

## Setup rápido
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ape plugins install solidity hardhat arbitrum
mkdir -p lib && cd lib && git clone --depth=1 https://github.com/OpenZeppelin/openzeppelin-contracts.git && cd ..
cp .env.example .env

## Deploy (Arbitrum Sepolia)
ape compile
ape run scripts/deploy.py --network arbitrum:sepolia
ape run scripts/deploy_strategies.py --network arbitrum:sepolia
ape run scripts/rebalance.py --network arbitrum:sepolia