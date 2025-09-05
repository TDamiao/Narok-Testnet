from ape import accounts, project
from ape.logging import logger
from dotenv import load_dotenv
import os

USDC_DEFAULT = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"

def main():
    load_dotenv()
    pk = os.getenv("PRIVATE_KEY")
    dev = os.getenv("DEV_TREASURY")
    sus = os.getenv("SUSTAIN_TREASURY")
    keeper = os.getenv("KEEPER_ADDRESS")
    min_secs = os.getenv("MIN_POKE_SECONDS")
    usdc = os.getenv("USDC_ADDRESS", USDC_DEFAULT)

    if not pk:
        raise RuntimeError("PRIVATE_KEY não definido no .env")
    if not dev or not sus:
        raise RuntimeError("Defina DEV_TREASURY e SUSTAIN_TREASURY no .env")

    acct = accounts.from_key(pk)
    logger.info(f"Deployer: {acct.address}")
    logger.info(f"USDC (asset): {usdc}")

    vault = acct.deploy(project.NarokVault, usdc, dev, sus)
    logger.info(f"NAROK Vault (NK): {vault.address}")

    if keeper:
        vault.setKeeper(keeper, sender=acct)
        logger.info(f"Keeper configurado: {keeper}")
    if min_secs:
        vault.setMinPokeInterval(int(min_secs), sender=acct)
        logger.info(f"minPokeInterval: {min_secs} s")

    print("\n=== Endereços ===")
    print("USDC:", usdc)
    print("VAULT (NK):", vault.address)