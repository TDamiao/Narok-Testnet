from ape import accounts, project
from ape.logging import logger
from dotenv import load_dotenv
import os
load_dotenv()
DEV_TREASURY=os.getenv("DEV_TREASURY"); SUSTAIN_TREASURY=os.getenv("SUSTAIN_TREASURY"); PRIVATE_KEY=os.getenv("PRIVATE_KEY")
def main():
    if not PRIVATE_KEY: raise RuntimeError("Set PRIVATE_KEY in .env")
    if not (DEV_TREASURY and SUSTAIN_TREASURY): raise RuntimeError("Set DEV_TREASURY and SUSTAIN_TREASURY in .env")
    acct=accounts.from_key(PRIVATE_KEY); logger.info(f"Deployer: {acct.address}")
    usdc=acct.deploy(project.MockStable,"Mock USDC","USDC",6); usdt=acct.deploy(project.MockStable,"Mock USDT","USDT",6)
    logger.info(f"USDC: {usdc.address}\nUSDT: {usdt.address}")
    vault=acct.deploy(project.NarokVault,usdc.address,DEV_TREASURY,SUSTAIN_TREASURY); logger.info(f"Vault: {vault.address}")
    usdc.faucet(acct.address,400_000*10**6,sender=acct); usdc.approve(vault.address,2**256-1,sender=acct); vault.deposit(200_000*10**6,acct.address,sender=acct)
    logger.info(f"Deposited 200k USDC -> NK minted. Shares total: {vault.totalSupply()}")
    print("\n=== Addresses ==="); print("USDC:",usdc.address); print("USDT:",usdt.address); print("VAULT:",vault.address)