// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title NarokVault (ERC-4626)
/// @notice Shares = NK. Asset = stable (USDC/USDT mock em testnet).
/// AUM fee 1%/ano (streaming) → mint de shares para devs; saída 2% no redeem (1% devs, 1% sustain).
contract NarokVault is ERC4626, Ownable {
    uint256 public constant YEAR = 365 days;

    // fees em partes por milhão (ppm). 1% = 10_000 ppm;
    uint256 public aumFeePpm = 10_000; // 1%
    uint256 public exitFeePpm = 20_000; // 2%

    address public devTreasury;
    address public sustainTreasury;

    uint256 public lastAccrual;

    error InvalidAddress();
    error ZeroAmount();

    event Accrued(uint256 feeShares);
    event SetAumFee(uint256 ppm);
    event SetExitFee(uint256 ppm);
    event SetTreasuries(address dev, address sustain);

    constructor(IERC20 _asset, address _dev, address _sustain)
        ERC20("Narok", "NK")
        ERC4626(_asset)
    {
        if (_dev == address(0) || _sustain == address(0)) revert InvalidAddress();
        devTreasury = _dev;
        sustainTreasury = _sustain;
        lastAccrual = block.timestamp;
    }

    // --- Admin ---
    function setAumFee(uint256 ppm) external onlyOwner {
        require(ppm <= 50_000, "max 5%/ano");
        aumFeePpm = ppm;
        emit SetAumFee(ppm);
    }
    function setExitFee(uint256 ppm) external onlyOwner {
        require(ppm <= 50_000, "max 5%");
        exitFeePpm = ppm;
        emit SetExitFee(ppm);
    }
    function setTreasuries(address _dev, address _sustain) external onlyOwner {
        if (_dev == address(0) || _sustain == address(0)) revert InvalidAddress();
        devTreasury = _dev;
        sustainTreasury = _sustain;
        emit SetTreasuries(_dev, _sustain);
    }

    // --- AUM accrual ---
    function _accrueAUM() internal {
        uint256 dt = block.timestamp - lastAccrual;
        if (dt == 0) return;
        lastAccrual = block.timestamp;
        // feeShares = totalShares * (aumFee * dt / YEAR)
        uint256 ts = totalSupply();
        if (ts == 0) return;
        uint256 feeShares = (ts * aumFeePpm * dt) / (1_000_000 * YEAR);
        if (feeShares > 0) {
            _mint(devTreasury, feeShares); // pode-se dividir com sustain se desejado
            emit Accrued(feeShares);
        }
    }

    // Hooks
    function deposit(uint256 assets, address receiver) public override returns (uint256) {
        _accrueAUM();
        require(assets > 0, "zero");
        return super.deposit(assets, receiver);
    }

    function mint(uint256 shares, address receiver) public override returns (uint256) {
        _accrueAUM();
        require(shares > 0, "zero");
        return super.mint(shares, receiver);
    }

    // Saída com taxa de 2% dividida 1%/1%
    function redeem(uint256 shares, address receiver, address owner_) public override returns (uint256 assetsOut) {
        _accrueAUM();
        require(shares > 0, "zero");
        // primeiro, retirar assets para o próprio vault
        uint256 previewAssets = previewRedeem(shares);
        _withdraw(_msgSender(), owner_, address(this), shares, previewAssets);
        uint256 fee = (previewAssets * exitFeePpm) / 1_000_000;
        uint256 feeDev = fee / 2;
        uint256 feeSustain = fee - feeDev;
        IERC20 assetToken = IERC20(asset());
        if (feeDev > 0) assetToken.transfer(devTreasury, feeDev);
        if (feeSustain > 0) assetToken.transfer(sustainTreasury, feeSustain);
        assetsOut = previewAssets - fee;
        assetToken.transfer(receiver, assetsOut);
    }

    // Opcional: override withdraw de forma similar
    function withdraw(uint256 assets, address receiver, address owner_) public override returns (uint256 shares) {
        _accrueAUM();
        uint256 previewShares = previewWithdraw(assets);
        // converte shares -> assets e aplica taxa equivalente no montante de assets
        _withdraw(_msgSender(), owner_, address(this), previewShares, assets);
        uint256 fee = (assets * exitFeePpm) / 1_000_000;
        uint256 feeDev = fee / 2;
        uint256 feeSustain = fee - feeDev;
        IERC20 assetToken = IERC20(asset());
        if (feeDev > 0) assetToken.transfer(devTreasury, feeDev);
        if (feeSustain > 0) assetToken.transfer(sustainTreasury, feeSustain);
        assetToken.transfer(receiver, assets - fee);
        return previewShares;
    }
}