from ape import accounts, project
from dotenv import load_dotenv
import os
load_dotenv(); PRIVATE_KEY=os.getenv("PRIVATE_KEY")
def main(amount:int=1000):
    acct=accounts.from_key(PRIVATE_KEY); usdc=project.MockStable.deployments[-1]; vault=project.NarokVault.deployments[-1]
    usdc.faucet(acct.address,amount*10**6,sender=acct); usdc.approve(vault.address,2**256-1,sender=acct); vault.deposit(amount*10**6,acct.address,sender=acct)
    print(f"Deposited {amount} USDC -> Minted NK to {acct.address}")