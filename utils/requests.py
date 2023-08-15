from typing import List, Optional

from eth_utils import encode_hex, function_abi_to_4byte_selector, add_0x_prefix
from web3 import Web3
from web3._utils.abi import get_abi_output_types
from web3._utils.contracts import encode_abi
from web3.types import HexBytes, BlockIdentifier

encode_hex_fn_abi = lambda fn_abi: encode_hex(
    function_abi_to_4byte_selector(fn_abi)
)

RAIN_MAKER_ADDRESS = '0x5CB93C0AdE6B7F2760Ec4389833B0cCcb5e4efDa'
CHAINLINK_ORACLES_ADDRESS = '0x7c37BF8dBd4Ae90cdf45d382cEB1580c5d9300CC'  # Used for MMs price
UNISWAP_ANCHORED_VIEW_ADDRESS = '0x16E340A4aa8b9089D0804010168986b624C805Bb'  # Used for COMP. (BANANA) price

# -=-=-=-=-=-=-=-=-=-=-=-=-=-
# UNISWAP_ANCHORED_VIEW | Price ABI
# -=-=-=-=-=-=-=-=-=-=-=-=-=-
PRICE_ABI = {"inputs": [{"internalType": "string", "name": "symbol", "type": "string"}], "name": "price",
             "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view",
             "type": "function"}
price_selector = encode_hex_fn_abi(PRICE_ABI)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-
# CHAINLINK_ORACLES | Get underlying price ABI
# -=-=-=-=-=-=-=-=-=-=-=-=-=-
GET_UNDERLYING_PRICE_ABI = {"inputs": [{"internalType": "address", "name": "cToken", "type": "address"}],
                            "name": "getUnderlyingPrice",
                            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                            "stateMutability": "view", "type": "function"}
get_underlying_price_selector = encode_hex_fn_abi(GET_UNDERLYING_PRICE_ABI)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-
# RAIN_MAKER | Comp. supply speeds ABI
# -=-=-=-=-=-=-=-=-=-=-=-=-=-
COMP_SUPPLY_SPEEDS_ABI = {"constant": True, "inputs": [{"internalType": "address", "name": "", "type": "address"}],
                          "name": "compSupplySpeeds",
                          "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "payable": False,
                          "stateMutability": "view", "type": "function"}
comp_supply_speeds_selector = encode_hex_fn_abi(COMP_SUPPLY_SPEEDS_ABI)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-
# MM | Supply Rate ABI
# -=-=-=-=-=-=-=-=-=-=-=-=-=-
SUPPLY_RATE_PER_BLOCK_ABI = {"constant": True, "inputs": [], "name": "supplyRatePerBlock",
                             "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "payable": False,
                             "stateMutability": "view", "type": "function"}
supply_rate_per_block_selector = encode_hex_fn_abi(SUPPLY_RATE_PER_BLOCK_ABI)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-
# MM | Total Supply ABI
# -=-=-=-=-=-=-=-=-=-=-=-=-=-
TOTAL_SUPPLY_ABI = {"constant": True, "inputs": [], "name": "totalSupply",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "payable": False,
                    "stateMutability": "view", "type": "function"}
total_supply_selector = encode_hex_fn_abi(TOTAL_SUPPLY_ABI)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-
# MM | Exchange Rate ABI
# -=-=-=-=-=-=-=-=-=-=-=-=-=-
EXCHANGE_RATE_ABI = {"constant": True, "inputs": [], "name": "exchangeRateStored",
                     "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "payable": False,
                     "stateMutability": "view", "type": "function"}
exchange_rate_selector = encode_hex_fn_abi(EXCHANGE_RATE_ABI)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-
# MULTICALL | Try Aggregate ABI
# -=-=-=-=-=-=-=-=-=-=-=-=-=-
TRY_AGGREGATE_ABI = {"inputs": [{"name": "requireSuccess", "type": "bool"}, {
    "components": [{"name": "target", "type": "address"}, {"name": "callData", "type": "bytes"}], "name": "calls",
    "type": "tuple[]"}], "name": "tryAggregate", "outputs": [
    {"components": [{"name": "success", "type": "bool"}, {"name": "returnData", "type": "bytes"}], "name": "returnData",
     "type": "tuple[]"}], "stateMutability": "nonpayable", "type": "function"}
try_aggregate_selector = encode_hex_fn_abi(TRY_AGGREGATE_ABI)
try_aggregate_output_types = get_abi_output_types(TRY_AGGREGATE_ABI)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-
# MULTICALL | Get block number ABI
# -=-=-=-=-=-=-=-=-=-=-=-=-=-
GET_BLOCK_NUMBER_ABI = {"inputs": [], "name": "getBlockNumber",
                        "outputs": [{"internalType": "uint256", "name": "blockNumber", "type": "uint256"}],
                        "stateMutability": "view", "type": "function"}
get_block_number_selector = encode_hex_fn_abi(GET_BLOCK_NUMBER_ABI)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-
# MULTICALL | Get current block timestamp ABI
# -=-=-=-=-=-=-=-=-=-=-=-=-=-
GET_CURRENT_BLOCK_TIMESTAMP_ABI = {"inputs": [], "name": "getCurrentBlockTimestamp",
                                   "outputs": [{"internalType": "uint256", "name": "timestamp", "type": "uint256"}],
                                   "stateMutability": "view", "type": "function"}
get_current_block_timestamp_selector = encode_hex_fn_abi(GET_CURRENT_BLOCK_TIMESTAMP_ABI)


def multicall_get_supply_rate(
        web3: Web3,
        multicall_address: str,
        mm_addresses: List[str],
        block_identifier: Optional[BlockIdentifier] = None,
) -> dict:
    # Requests to MM contracts
    encoded = [
        (
            address,
            encode_abi(
                web3,
                SUPPLY_RATE_PER_BLOCK_ABI,
                arguments=(),
                data=supply_rate_per_block_selector,
            ),
        )
        for address in mm_addresses
    ]
    encoded = encoded + [
        (
            address,
            encode_abi(
                web3,
                TOTAL_SUPPLY_ABI,
                arguments=(),
                data=total_supply_selector,
            ),
        )
        for address in mm_addresses
    ]
    encoded = encoded + [
        (
            address,
            encode_abi(
                web3,
                EXCHANGE_RATE_ABI,
                arguments=(),
                data=exchange_rate_selector,
            ),
        )
        for address in mm_addresses
    ]

    # Requests to ChainLink oracles contract
    encoded = encoded + [
        (
            CHAINLINK_ORACLES_ADDRESS,
            encode_abi(
                web3,
                GET_UNDERLYING_PRICE_ABI,
                arguments=[address],
                data=get_underlying_price_selector,
            ),
        )
        for address in mm_addresses
    ]

    # Requests to RainMaker contract
    encoded = encoded + [
        (
            RAIN_MAKER_ADDRESS,
            encode_abi(
                web3,
                COMP_SUPPLY_SPEEDS_ABI,
                arguments=[address],
                data=comp_supply_speeds_selector,
            ),
        )
        for address in mm_addresses
    ]

    # Requests to Uniswap Anchored View contract
    encoded = encoded + [
        (
            UNISWAP_ANCHORED_VIEW_ADDRESS,
            encode_abi(
                web3,
                PRICE_ABI,
                arguments=['BANANA'],
                data=price_selector,
            ),
        )
    ]

    # Requests to Multicall contract itself
    encoded = encoded + [
        (
            multicall_address,
            encode_abi(
                web3,
                GET_BLOCK_NUMBER_ABI,
                arguments=(),
                data=get_block_number_selector,
            ),
        ),
        (
            multicall_address,
            encode_abi(
                web3,
                GET_CURRENT_BLOCK_TIMESTAMP_ABI,
                arguments=(),
                data=get_current_block_timestamp_selector,
            ),
        )
    ]

    data = add_0x_prefix(
        encode_abi(
            web3,
            TRY_AGGREGATE_ABI,
            (False, [(address, enc) for address, enc in encoded]),
            try_aggregate_selector,
        )
    )
    tx_raw_data = web3.eth.call({"to": multicall_address, "data": data}, block_identifier=block_identifier)
    output_data = web3.codec.decode(try_aggregate_output_types, tx_raw_data)[0]
    output_data = (
        str(web3.codec.decode(["uint256"], HexBytes(raw_output))[0]) for (_, raw_output) in output_data
    )

    fields = mm_addresses[:]
    fields += [address + '_total_supply' for address in mm_addresses]
    fields += [address + '_exchange_rate' for address in mm_addresses]
    fields += [address + '_price' for address in mm_addresses]
    fields += [address + '_comp_supply_speeds' for address in mm_addresses]
    fields += ['BANANA_price', 'blockNumber', 'blockTimestamp']

    return dict(zip(fields, output_data))
