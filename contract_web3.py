from dotenv import load_dotenv
from web3 import Web3
import os

# Load environment variables from .env file
load_dotenv()

# Connecting to an Ethereum node provided by QuickNode
w3 = Web3(Web3.HTTPProvider( os.getenv("INFURA_RPC_URL")))
#w3 = Web3(Web3.HTTPProvider("https://polygon-mumbai.infura.io/v3/d26ad05ad2c54b9991e83933ff9054a7"))


def get_token_balance(address, contract_address):
    # ERC20 Contract ABI
    ERC20_ABI = '''
    [
        {
            "constant":true,
            "inputs":[{"name":"_owner","type":"address"}],
            "name":"balanceOf",
            "outputs":[{"name":"balance","type":"uint256"}],
            "type":"function"
        },
        {
            "constant":true,
            "inputs":[],
            "name":"decimals",
            "outputs":[{"name":"","type":"uint8"}],
            "type":"function"
        }
    ]
    '''
    
    # Creating contract instance
    contract = w3.eth.contract(address=contract_address, abi=ERC20_ABI)
    
    # Call balanceOf function from the contract
    balance = contract.functions.balanceOf(address).call()
    
    # Get the token's decimals
    decimals = contract.functions.decimals().call()
    decimals = 18
    
    # Adjust for the token's decimal places
    balance = balance / (10 ** decimals)
    
    return balance

