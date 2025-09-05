from ape import accounts, project
from dotenv import load_dotenv
import os
load_dotenv(); PRIVATE_KEY=os.getenv("PRIVATE_KEY")
def main():
    accounts.from_key(PRIVATE_KEY); vault=project.NarokVault.deployments[-1]; asset=project.MockStable.at(vault.asset())
    total=vault.totalAssets(); cash=asset.balanceOf(vault.address); n=vault.strategiesLength()
    print("Total Assets:",total); print("Cash (vault):",cash); print("Strategies:",n)
    for i in range(n):
        (strat,weight,active)=vault.strats(i); if not active: continue
        bal=project.SimpleStrategy.at(strat).totalAssets(); print(f"[{i}] strat={strat} weight={weight}bps bal={bal}")