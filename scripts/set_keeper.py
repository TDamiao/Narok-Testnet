from ape import accounts, project
from dotenv import load_dotenv
import os
load_dotenv(); PRIVATE_KEY=os.getenv("PRIVATE_KEY")
def main(keeper:str=None):
    if not keeper: keeper=os.getenv("KEEPER_ADDRESS")
    if not keeper: raise RuntimeError("Pass --keeper 0x... or set KEEPER_ADDRESS in .env")
    acct=accounts.from_key(PRIVATE_KEY); vault=project.NarokVault.deployments[-1]
    vault.setKeeper(keeper,sender=acct); print("Keeper set to:",keeper)