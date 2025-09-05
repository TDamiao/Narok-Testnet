from ape import accounts, project
from dotenv import load_dotenv
import os
load_dotenv(); PRIVATE_KEY=os.getenv("PRIVATE_KEY")
def main(seconds:int=21600):
    acct=accounts.from_key(PRIVATE_KEY); vault=project.NarokVault.deployments[-1]
    vault.setMinPokeInterval(int(seconds),sender=acct); print("minPokeInterval set to",seconds,"seconds")