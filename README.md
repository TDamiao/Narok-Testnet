# Narok • Ape (Python) – Testnet Starter

Vault ERC‑4626 com token de cota **NK**, taxa AUM **1%/ano** (streaming) e taxa de saída **2%** (1% devs, 1% sustentabilidade).
Scripts Python (Ape) para **deploy na Arbitrum Sepolia**, cunho de mocks USDC/USDT e **depósito** no vault.

> ⚠️ Uso exclusivo em **TESTNET** neste repositório. Para mainnet, faça auditoria e revisões de segurança.

---

## 📦 Setup

1) Python 3.10+ e `pip` prontos.  
2) Instale dependências:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ape plugins install solidity hardhat arbitrum
```
3) Instale OpenZeppelin em vendor para os imports:
```bash
mkdir -p lib
cd lib && git clone --depth=1 https://github.com/OpenZeppelin/openzeppelin-contracts.git
cd ..
```
4) Configure o `.env`:
```bash
cp .env.example .env
# edite PRIVATE_KEY, ARB_SEPOLIA_RPC, DEV_TREASURY, SUSTAIN_TREASURY
```

## 🔧 Compilar
```bash
ape compile
```

## 🚀 Deploy (Arbitrum Sepolia)
```bash
ape run scripts/deploy.py --network arbitrum:sepolia
```
O script:
- Deploy `MockUSDC` (6 decimais) e `MockUSDT` (6 decimais);
- Deploy `NarokVault` (asset = USDC mock, fee AUM 1%/ano, fee de saída 2% dividido);
- Cunha USDC para a carteira e faz `deposit()` para criar NK inicial.

## 💸 Testar Depósito
```bash
ape run scripts/deposit_usdc.py --network arbitrum:sepolia --amount 1000
ape run scripts/deposit_usdt.py --network arbitrum:sepolia --amount 500
```
> Em testnet USDT→USDC é simulado via **mocks**; em produção, troque por rota via DEX/Router.

## 🔁 Resgatar (com taxa de saída 2%)
```bash
ape run scripts/redeem.py --network arbitrum:sepolia --shares 100
```

## 🧪 Notas
- A taxa AUM é **acumulada continuamente** e materializada ao interagir (mint/redeem).
- A taxa de **saída** (2%) é aplicada no `redeem()` e enviada 1% para `DEV_TREASURY` e 1% para `SUSTAIN_TREASURY`.
- Para aceitar USDT em produção, utilize um **router** que troque USDT→USDC via DEX, então chame `vault.deposit()`.

---

## ⚠️ Segurança
- Ative multisig e timelock para tesourarias.
- Escreva testes e faça auditoria externa antes de mainnet.