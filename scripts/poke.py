from ape import accounts, project
from dotenv import load_dotenv
import os
load_dotenv(); PRIVATE_KEY=os.getenv("PRIVATE_KEY")
def main():
    acct=accounts.from_key(PRIVATE_KEY); vault=project.NarokVault.deployments[-1]
    print("needsPoke():",vault.needsPoke()); tx=vault.poke(sender=acct); print("poke() sent. tx:",tx.txn_hash.hex())