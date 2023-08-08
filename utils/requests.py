from typing import List, Optional

from eth_utils import encode_hex, function_abi_to_4byte_selector, add_0x_prefix
from web3 import Web3
from web3._utils.abi import get_abi_output_types
from web3._utils.contracts import encode_abi
from web3.types import HexBytes, BlockIdentifier

encode_hex_fn_abi = lambda fn_abi: encode_hex(
    function_abi_to_4byte_selector(fn_abi)
)

SUPPLY_RATE_PER_BLOCK_ABI = {"constant": True, "inputs": [], "name": "supplyRatePerBlock",
                             "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "payable": False,
                             "stateMutability": "view", "type": "function"}
supply_rate_per_block_selector = encode_hex_fn_abi(SUPPLY_RATE_PER_BLOCK_ABI)

TRY_AGGREGATE_ABI = {"inputs": [{"name": "requireSuccess", "type": "bool"}, {
    "components": [{"name": "target", "type": "address"}, {"name": "callData", "type": "bytes"}], "name": "calls",
    "type": "tuple[]"}], "name": "tryAggregate", "outputs": [
    {"components": [{"name": "success", "type": "bool"}, {"name": "returnData", "type": "bytes"}], "name": "returnData",
     "type": "tuple[]"}], "stateMutability": "nonpayable", "type": "function"}
try_aggregate_selector = encode_hex_fn_abi(TRY_AGGREGATE_ABI)
try_aggregate_output_types = get_abi_output_types(TRY_AGGREGATE_ABI)

GET_BLOCK_NUMBER_ABI = {"inputs": [], "name": "getBlockNumber",
                        "outputs": [{"internalType": "uint256", "name": "blockNumber", "type": "uint256"}],
                        "stateMutability": "view", "type": "function"}
get_block_number_selector = encode_hex_fn_abi(GET_BLOCK_NUMBER_ABI)

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
            (False, [(token_addr, enc) for token_addr, enc in encoded]),
            try_aggregate_selector,
        )
    )
    tx_raw_data = web3.eth.call({"to": multicall_address, "data": data}, block_identifier=block_identifier)
    output_data = web3.codec.decode(try_aggregate_output_types, tx_raw_data)[0]
    output_data = (
        str(web3.codec.decode(["uint256"], HexBytes(raw_output))[0]) for (_, raw_output) in output_data
    )
    return dict(zip(mm_addresses + ['blockNumber', 'blockTimestamp'], output_data))
