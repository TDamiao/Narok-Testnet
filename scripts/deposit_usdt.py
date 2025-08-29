from ape import accounts, project
from dotenv import load_dotenv
import os

load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

def main(amount: int = 500):
    acct = accounts.from_key(PRIVATE_KEY)
    usdt = project.MockStable.deployments[-1]  # careful: ensure it's USDT index if multiple
    vault = project.NarokVault.deployments[-1]
    # For demo: mint USDT to user, then SIMULATE a 1:1 conversion by minting USDC and burning USDT in your backend/workflow.
    # In production, replace with a DEX swap and then call vault.deposit().
    # Here, we just faucet USDC and deposit (since mocks are under our control).
    usdc = project.MockStable.at(vault.asset())
    # faucet USDT (visual), then faucet USDC for real deposit
    usdt.faucet(acct.address, amount * 10**6, sender=acct)
    usdc.faucet(acct.address, amount * 10**6, sender=acct)
    usdc.approve(vault.address, 2**256-1, sender=acct)
    vault.deposit(amount * 10**6, acct.address, sender=acct)
    print(f"[Test] Deposited {amount} (via USDT->USDC mock) -> Minted NK to {acct.address}")