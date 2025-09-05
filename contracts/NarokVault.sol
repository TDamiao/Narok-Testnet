// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;
import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
interface IStrat{function totalAssets() external view returns(uint256);function withdrawToVault(uint256 amount) external returns(uint256);}
contract NarokVault is ERC4626, Ownable {
    uint256 public constant YEAR=365 days; uint256 public constant MAX_BPS=10_000;
    uint256 public aumFeePpm=10_000; uint256 public exitFeePpm=20_000;
    address public devTreasury; address public sustainTreasury;
    address public keeper; uint256 public minPokeInterval=6 hours; uint256 public lastAccrual;
    struct StratInfo{address strat; uint16 weightBps; bool active;} StratInfo[] public strats; mapping(address=>uint256) public stratIndex; uint16 public totalWeightBps;
    event Accrued(uint256 feeShares); event Poked(address indexed caller,uint256 elapsed,uint256 feeShares);
    event SetAumFee(uint256 ppm); event SetExitFee(uint256 ppm); event SetTreasuries(address dev,address sustain);
    event SetKeeper(address keeper); event SetMinPokeInterval(uint256 s); event AddStrategy(address strat,uint16 w);
    event SetStrategyWeight(address strat,uint16 w); event RemoveStrategy(address strat); event Rebalanced(uint256 cashBefore,uint256 cashAfter);
    error InvalidAddress(); error StrategyExists(); error StrategyNotFound(); error WeightOverflow();
    constructor(IERC20 _asset,address _dev,address _sustain) ERC20("Narok","NK") ERC4626(_asset){if(_dev==address(0)||_sustain==address(0)) revert InvalidAddress();devTreasury=_dev;sustainTreasury=_sustain;lastAccrual=block.timestamp;}
    function setAumFee(uint256 ppm) external onlyOwner{require(ppm<=50_000,"max 5%/ano"); aumFeePpm=ppm; emit SetAumFee(ppm);}
    function setExitFee(uint256 ppm) external onlyOwner{require(ppm<=50_000,"max 5%"); exitFeePpm=ppm; emit SetExitFee(ppm);}
    function setTreasuries(address _d,address _s) external onlyOwner{if(_d==address(0)||_s==address(0)) revert InvalidAddress(); devTreasury=_d; sustainTreasury=_s; emit SetTreasuries(_d,_s);}
    function setKeeper(address k) external onlyOwner{if(k==address(0)) revert InvalidAddress(); keeper=k; emit SetKeeper(k);}
    function setMinPokeInterval(uint256 sec) external onlyOwner{require(sec<=30 days,"interval too big"); minPokeInterval=sec; emit SetMinPokeInterval(sec);}
    function addStrategy(address s,uint16 w) external onlyOwner{if(s==address(0)) revert InvalidAddress(); if(stratIndex[s]!=0) revert StrategyExists(); uint16 newTotal=totalWeightBps+w; if(newTotal>MAX_BPS) revert WeightOverflow(); strats.push(StratInfo({strat:s,weightBps:w,active:true})); stratIndex[s]=strats.length; totalWeightBps=newTotal; emit AddStrategy(s,w);}
    function setStrategyWeight(address s,uint16 w) external onlyOwner{uint256 idx=stratIndex[s]; if(idx==0) revert StrategyNotFound(); StratInfo storage info=strats[idx-1]; uint16 old=info.weightBps; uint16 newTotal=totalWeightBps+w-old; if(newTotal>MAX_BPS) revert WeightOverflow(); info.weightBps=w; totalWeightBps=newTotal; emit SetStrategyWeight(s,w);}
    function removeStrategy(address s) external onlyOwner{uint256 idx=stratIndex[s]; if(idx==0) revert StrategyNotFound(); StratInfo storage info=strats[idx-1]; if(info.active){info.active=false; totalWeightBps-=info.weightBps; info.weightBps=0;} emit RemoveStrategy(s);}
    function _accrueAUMInternal() internal returns(uint256 feeShares){uint256 dt=block.timestamp-lastAccrual; if(dt==0) return 0; lastAccrual=block.timestamp; uint256 ts=totalSupply(); if(ts==0) return 0; feeShares=(ts*aumFeePpm*dt)/(1_000_000*YEAR); if(feeShares>0){_mint(devTreasury,feeShares); emit Accrued(feeShares);}}
    function needsPoke() public view returns(bool){return block.timestamp-lastAccrual>=minPokeInterval;}
    function poke() external {uint256 elapsed=block.timestamp-lastAccrual; uint256 minted=_accrueAUMInternal(); if(msg.sender==keeper){_rebalance(0);} emit Poked(msg.sender,elapsed,minted);}
    function totalAssets() public view override returns(uint256){uint256 cash=IERC20(asset()).balanceOf(address(this)); for(uint256 i=0;i<strats.length;i++){StratInfo memory info=strats[i]; if(!info.active) continue; cash+=IStrat(info.strat).totalAssets();} return cash;}
    function deposit(uint256 assets,address receiver) public override returns(uint256){_accrueAUMInternal(); require(assets>0,"zero"); return super.deposit(assets,receiver);}
    function mint(uint256 shares,address receiver) public override returns(uint256){_accrueAUMInternal(); require(shares>0,"zero"); return super.mint(shares,receiver);}
    function redeem(uint256 shares,address receiver,address owner_) public override returns(uint256 out){_accrueAUMInternal(); require(shares>0,"zero"); uint256 pre=previewRedeem(shares); _withdraw(_msgSender(),owner_,address(this),shares,pre); uint256 fee=(pre*exitFeePpm)/1_000_000; uint256 fd=fee/2; uint256 fs=fee-fd; IERC20 a=IERC20(asset()); if(fd>0)a.transfer(devTreasury,fd); if(fs>0)a.transfer(sustainTreasury,fs); out=pre-fee; a.transfer(receiver,out);}
    function withdraw(uint256 assets,address receiver,address owner_) public override returns(uint256 sh){_accrueAUMInternal(); uint256 pre=previewWithdraw(assets); _withdraw(_msgSender(),owner_,address(this),pre,assets); uint256 fee=(assets*exitFeePpm)/1_000_000; uint256 fd=fee/2; uint256 fs=fee-fd; IERC20 a=IERC20(asset()); if(fd>0)a.transfer(devTreasury,fd); if(fs>0)a.transfer(sustainTreasury,fs); a.transfer(receiver,assets-fee); return pre;}
    function _rebalance(uint256 minMove) internal {IERC20 a=IERC20(asset()); uint256 tot=totalAssets(); uint256 cashStart=a.balanceOf(address(this));
        for(uint256 i=0;i<strats.length;i++){StratInfo memory info=strats[i]; if(!info.active) continue; uint256 target=(tot*info.weightBps)/MAX_BPS; uint256 cur=IStrat(info.strat).totalAssets(); if(cur>target+minMove){uint256 ex=cur-target; IStrat(info.strat).withdrawToVault(ex);}}
        uint256 cash=a.balanceOf(address(this));
        for(uint256 i=0;i<strats.length;i++){StratInfo memory info=strats[i]; if(!info.active) continue; uint256 target=(tot*info.weightBps)/MAX_BPS; uint256 cur=IStrat(info.strat).totalAssets(); if(cur+minMove<target){uint256 def=target-cur; if(def>cash) def=cash; if(def>minMove){a.transfer(info.strat,def); cash-=def;}}}
        emit Rebalanced(cashStart,a.balanceOf(address(this)));}
    function rebalance(uint256 minMove) external {require(msg.sender==keeper||msg.sender==owner(),"not auth"); _rebalance(minMove);}
}