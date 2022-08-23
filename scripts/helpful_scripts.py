from brownie import (
    network,
    config,
    accounts,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface,
)

FORKED_ENVIRONMENTS = ["mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
DECIMALS = 8
STARTING_PRICE = 200000000000


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)  # here we are using local created networks
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_ENVIRONMENTS
    ):
        print("This is " + str(accounts))
        return accounts[0]
    # here is reference to private key hiddden in .env, because we are using real test network
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and
    return that mock contract.
        Args:
            contract_name (string)
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    print(contract_name)
    print(network.show_active())
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]  # = MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        print(contract_address)
        # address
        # ABI
        if network.show_active() == "rinkeby":
            contract = Contract.from_abi(
                "eth_usd_price_feed", contract_address, contract_type.abi
            )
        else:
            contract = Contract.from_abi(
                contract_type.name, contract_address, contract_type.abi
            )
    return contract


def deploy_mocks(decimals=DECIMALS, initial_value=STARTING_PRICE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("\nThis is " + str(account))


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    # 0.1 LINK
    account = (
        account if account else get_account()
    )  # account that we use is gonna be this account thing even exist otherwise we'll call our get_account
    link_token = (
        link_token if link_token else get_contract("link_token")
    )  # to samo po polsku: jeśli nie mamy gotowego link_tokena musimy wywołać funkcję get aby go otrzymać
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # To poniżej jest równowazne z tym --->  contract = Contract.from_abi(contract_type.name, contract_address, contract_type.abi)
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!" + str(account))
    return tx
