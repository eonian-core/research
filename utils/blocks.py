def get_year_old_block(web3, seconds_per_block):
    seconds_per_year = 365 * 24 * 60 * 60
    blocks_per_year = seconds_per_year / seconds_per_block

    latest_block = web3.eth.block_number
    year_old_block = int(latest_block - blocks_per_year)

    return web3.eth.get_block(year_old_block)
