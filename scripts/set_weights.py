from ape import accounts, project
from dotenv import load_dotenv
import os
load_dotenv(); PRIVATE_KEY=os.getenv("PRIVATE_KEY")
def main(w1:int=2500,w2:int=2500,w3:int=2500):
    acct=accounts.from_key(PRIVATE_KEY); vault=project.NarokVault.deployments[-1]
    if vault.strategiesLength()<3: raise RuntimeError("Need at least 3 strategies deployed")
    s1=vault.strats(0)[0]; s2=vault.strats(1)[0]; s3=vault.strats(2)[0]
    total=int(w1)+int(w2)+int(w3); if total>10000: raise RuntimeError("Sum of weights must be <= 10000")
    vault.setStrategyWeight(s1,int(w1),sender=acct); vault.setStrategyWeight(s2,int(w2),sender=acct); vault.setStrategyWeight(s3,int(w3),sender=acct)
    print("Weights updated:",w1,w2,w3,"| Cash =",10000-total)