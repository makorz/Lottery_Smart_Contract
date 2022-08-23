from scripts.helpful_scripts import *
from brownie import Lottery, network, config
import time


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},  # to oznnacza kto jest twórcą kontraktu
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("\nDeployed Lotteryyyyyy\n")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    print(lottery)
    # Need to wait to end last transaction
    lottery.startLottery({"from": account}).wait(1)
    print("\nLottery has started!!!\n")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    lottery.enter({"from": account, "value": value}).wait(1)
    print("\nYou entered the lottery!\n")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    print(str(lottery))
    # fund the contract
    # then end the lottery
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(240)
    print(f"\n{lottery.recentWinner()} is winner!")
    print(f"\n{lottery.randomness()} is random!")
    print(f"\n{lottery.usdEntryFee()} is usdFee!")
    print(f"\n{lottery.keyhash()} is keyhash!")
    print(f"\n{lottery.fee()} is fee!")
