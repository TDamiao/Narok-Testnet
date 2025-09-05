from ape import accounts, project, chain
from ape.logging import logger
from dotenv import load_dotenv
from web3 import Web3
from decimal import Decimal, getcontext
import os

UNISWAP_V3_FACTORY = Web3.to_checksum_address("0x1F98431c8aD98523631AE4a59f267346ea31F984")
NONFUNGIBLE_POSITION_MANAGER = Web3.to_checksum_address("0xC36442b4a4522E871399CD717aBDD847Ab11FE88")
USDC_DEFAULT = Web3.to_checksum_address("0xAf88d065E77c8Ccc2239327C5EDb3A432268e5831")

ERC20_ABI = [
    {"name":"decimals","inputs":[],"outputs":[{"type":"uint8"}],"stateMutability":"view","type":"function"},
    {"name":"approve","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"type":"bool"}],"stateMutability":"nonpayable","type":"function"},
    {"name":"balanceOf","inputs":[{"name":"account","type":"address"}],"outputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},
]

NPM_ABI = [
    {
        "inputs":[
            {"internalType":"address","name":"token0","type":"address"},
            {"internalType":"address","name":"token1","type":"address"},
            {"internalType":"uint24","name":"fee","type":"uint24"},
            {"internalType":"uint160","name":"sqrtPriceX96","type":"uint160"}
        ],
        "name":"createAndInitializePoolIfNecessary",
        "outputs":[{"internalType":"address","name":"pool","type":"address"}],
        "stateMutability":"payable",
        "type":"function"
    },
    {
        "inputs":[
            {
                "components":[
                    {"internalType":"address","name":"token0","type":"address"},
                    {"internalType":"address","name":"token1","type":"address"},
                    {"internalType":"uint24","name":"fee","type":"uint24"},
                    {"internalType":"int24","name":"tickLower","type":"int24"},
                    {"internalType":"int24","name":"tickUpper","type":"int24"},
                    {"internalType":"uint256","name":"amount0Desired","type":"uint256"},
                    {"internalType":"uint256","name":"amount1Desired","type":"uint256"},
                    {"internalType":"uint256","name":"amount0Min","type":"uint256"},
                    {"internalType":"uint256","name":"amount1Min","type":"uint256"},
                    {"internalType":"address","name":"recipient","type":"address"},
                    {"internalType":"uint256","name":"deadline","type":"uint256"}
                ],
                "internalType":"struct INonfungiblePositionManager.MintParams",
                "name":"params","type":"tuple"
            }
        ],
        "name":"mint",
        "outputs":[
            {"internalType":"uint256","name":"tokenId","type":"uint256"},
            {"internalType":"uint128","name":"liquidity","type":"uint128"},
            {"internalType":"uint256","name":"amount0","type":"uint256"},
            {"internalType":"uint256","name":"amount1","type":"uint256"}
        ],
        "stateMutability":"payable",
        "type":"function"
    }
]

def to_checksum(addr: str) -> str:
    return Web3.to_checksum_address(addr)

def as_int(addr: str) -> int:
    return int(addr, 16)

def compute_sqrt_price_x96(price_token1_per_token0: Decimal, dec0: int, dec1: int) -> int:
    getcontext().prec = 200
    ratio = price_token1_per_token0 * (Decimal(10) ** (dec1 - dec0))
    sqrt_ratio = ratio.sqrt()
    return int(sqrt_ratio * (1 << 96))

def main(price_usdc_per_nk: float = 1.0, fee: int = 3000, amount_usdc: float = 0, amount_nk: float = 0):
    load_dotenv()
    pk = os.getenv("PRIVATE_KEY")
    if not pk:
        raise RuntimeError("PRIVATE_KEY não definido no .env")
    acct = accounts.from_key(pk)

    usdc = to_checksum(os.getenv("USDC_ADDRESS", USDC_DEFAULT))
    nk_env = os.getenv("NAROK_ADDRESS")
    if nk_env:
        nk = to_checksum(nk_env)
    else:
        vault = project.NarokVault.deployments[-1]
        nk = to_checksum(vault.address)

    token0, token1 = (usdc, nk) if as_int(usdc) < as_int(nk) else (nk, usdc)

    erc0 = project.Contract(token0, abi=ERC20_ABI)
    erc1 = project.Contract(token1, abi=ERC20_ABI)
    dec0 = erc0.decimals()
    dec1 = erc1.decimals()

    from decimal import Decimal as D
    price_real = D(str(price_usdc_per_nk))
    if token0 == usdc and token1 == nk:
        price_t1_t0 = D(1) / price_real  # NK/USDC
    else:
        price_t1_t0 = price_real        # USDC/NK

    sqrt_price_x96 = compute_sqrt_price_x96(price_t1_t0, dec0, dec1)
    npm = project.Contract(NONFUNGIBLE_POSITION_MANAGER, abi=NPM_ABI)
    pool_addr = npm.createAndInitializePoolIfNecessary(token0, token1, int(fee), int(sqrt_price_x96), sender=acct, value=0)

    if (amount_usdc <= 0) and (amount_nk <= 0):
        print("\nPool criada/inicializada. Sem liquidez inicial (amounts=0).")
        print("Pool:", pool_addr)
        return

    spacing = {100:1, 500:10, 3000:60, 10000:200}.get(int(fee))
    if spacing is None:
        raise RuntimeError("fee inválida. Use 100 / 500 / 3000 / 10000")

    MIN_TICK, MAX_TICK = -887272, 887272
    lower = (MIN_TICK // spacing) * spacing
    upper = (MAX_TICK // spacing) * spacing

    amt0_h = D(str(amount_usdc)) if token0 == usdc else D(str(amount_nk))
    amt1_h = D(str(amount_usdc)) if token1 == usdc else D(str(amount_nk))
    amt0 = int(amt0_h * (D(10) ** dec0))
    amt1 = int(amt1_h * (D(10) ** dec1))

    erc0.approve(NONFUNGIBLE_POSITION_MANAGER, amt0, sender=acct)
    erc1.approve(NONFUNGIBLE_POSITION_MANAGER, amt1, sender=acct)

    deadline = chain.pending_timestamp + 1800
    params = {
        "token0": token0,
        "token1": token1,
        "fee": int(fee),
        "tickLower": int(lower),
        "tickUpper": int(upper),
        "amount0Desired": int(amt0),
        "amount1Desired": int(amt1),
        "amount0Min": 0,
        "amount1Min": 0,
        "recipient": acct.address,
        "deadline": int(deadline),
    }

    tokenId, liq, used0, used1 = npm.mint(params, sender=acct, value=0)
    print("\n=== LP NFT ===")
    print("tokenId:", tokenId, "| liquidity:", liq)
    print("amount0 used:", used0, "| amount1 used:", used1)
    print("Pool:", pool_addr)