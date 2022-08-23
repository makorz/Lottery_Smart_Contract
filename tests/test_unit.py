# 0,0059
# 59000000000000000
from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lotery import *
from scripts.helpful_scripts import *
from web3 import Web3
import pytest


def test_get_entrance_fee(lottery_contract):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    # Act
    # 1,850 eth / usd
    # usdEntryFee is 10
    # 1850/1 == 10/x == 0.025
    expected_entrance_fee = Web3.toWei(0.005, "ether")
    entrance_fee = lottery_contract.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee

    # Previous version:
    # account = accounts[0]
    # lottery = Lottery.deploy(
    #     config["networks"][network.show_active()]["eth_usd_price_feed"],
    #     {"from": account},
    # )
    # assert lottery.getEntranceFee() < 6100000000000000
    # assert lottery.getEntranceFee() > 5700000000000000
    # # with function counting in ether
    # assert lottery.getEntranceFee() < Web3.toWei(0.0061, "ether")
    # assert lottery.getEntranceFee() > Web3.toWei(0.0057, "ether")


def test_cant_enter_unless_started(lottery_contract):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery_contract.enter(
            {"from": get_account(), "value": lottery_contract.getEntranceFee()}
        )


def test_can_start_and_enter_lottery(lottery_contract):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    account = get_account()
    lottery_contract.startLottery({"from": account})
    # Act
    lottery_contract.enter(
        {"from": account, "value": lottery_contract.getEntranceFee()}
    )
    # Assert
    assert lottery_contract.players(0) == account


def test_can_pick_winner_correctly(lottery_contract):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    account = get_account()
    lottery_contract.startLottery({"from": account})
    lottery_contract.enter(
        {"from": account, "value": lottery_contract.getEntranceFee()}
    )
    lottery_contract.enter(
        {"from": get_account(index=1), "value": lottery_contract.getEntranceFee()}
    )
    lottery_contract.enter(
        {"from": get_account(index=2), "value": lottery_contract.getEntranceFee()}
    )
    fund_with_link(lottery_contract)
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery_contract.balance()
    transaction = lottery_contract.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery_contract.address, {"from": account}
    )
    # 777 % 3 = 0
    assert lottery_contract.recentWinner() == account
    assert lottery_contract.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
