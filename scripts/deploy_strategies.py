from ape import accounts, project
from dotenv import load_dotenv
import os
load_dotenv(); PRIVATE_KEY=os.getenv("PRIVATE_KEY")
W1=W2=W3=2500
def main():
    acct=accounts.from_key(PRIVATE_KEY); vault=project.NarokVault.deployments[-1]
    s1=acct.deploy(project.SimpleStrategy,vault.address); s2=acct.deploy(project.SimpleStrategy,vault.address); s3=acct.deploy(project.SimpleStrategy,vault.address)
    vault.addStrategy(s1.address,W1,sender=acct); vault.addStrategy(s2.address,W2,sender=acct); vault.addStrategy(s3.address,W3,sender=acct)
    print("Strategies:"); print("S1:",s1.address,"weight:",W1); print("S2:",s2.address,"weight:",W2); print("S3:",s3.address,"weight:",W3)