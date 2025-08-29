from ape import accounts, project
from dotenv import load_dotenv
import os

load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

def main(shares: int = 100):
    acct = accounts.from_key(PRIVATE_KEY)
    vault = project.NarokVault.deployments[-1]
    # approve NK (shares) to vault if necessary (ERC4626 uses transfer/burn internally)
    vault.approve(vault.address, 2**256-1, sender=acct)  # approves NK itself
    vault.redeem(shares * 10**18, acct.address, acct.address, sender=acct)
    print(f"Redeemed {shares} NK -> USDC (minus 2% exit fee)")