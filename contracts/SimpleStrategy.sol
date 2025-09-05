// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
interface IVaultView{function asset() external view returns(address);}
contract SimpleStrategy is Ownable {
    IVaultView public immutable vault; IERC20 public immutable asset;
    event WithdrawToVault(uint256 amount);
    constructor(address _vault){vault=IVaultView(_vault);asset=IERC20(vault.asset());_transferOwnership(msg.sender);}
    modifier onlyVault(){require(msg.sender==address(vault),"only vault");_;}
    function totalAssets() public view returns(uint256){return asset.balanceOf(address(this));}
    function withdrawToVault(uint256 amount) external onlyVault returns(uint256 w){uint256 b=asset.balanceOf(address(this));w=amount>b?b:amount;if(w>0){asset.transfer(address(vault),w);emit WithdrawToVault(w);}}
}