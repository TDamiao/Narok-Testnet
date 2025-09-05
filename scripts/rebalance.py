from ape import accounts, project
from dotenv import load_dotenv
import os
load_dotenv(); PRIVATE_KEY=os.getenv("PRIVATE_KEY")
def main(min_move:int=0):
    acct=accounts.from_key(PRIVATE_KEY); vault=project.NarokVault.deployments[-1]
    vault.rebalance(int(min_move),sender=acct); print("Rebalance executed with min_move:",min_move)