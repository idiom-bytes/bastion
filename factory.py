# import currency
#
# S = Hash()
#
# all_pairs = address[]
# pairs = all_pairs[token0][token1]
#
# token_interface = ...
#
# def validate_address(token: str):
# 	assert token[0:1] == '0x', 'ZERO ADDRESS'
#
# 	unique_chars = token[2:-1].get_unique_chars()
# 	assert len(unique_chars) > 1 and unique_chars[0] != '0', 'ZERO ADDRESS'
#
# @export
# def all_pairs_length():
# 	pair_length =  S.length()
# 	return pair_length
#
# # tokenA + tokenB are addresses
# def create_pair(tokenA: str, tokenB: str):
# 	assert tokenA != tokenB, 'IDENTICAL ADDRESSES'
# 	token0, token1 = (tokenA, tokenB) if tokenA < tokenB else (tokenB, tokenA)
#
# 	validate_address(token0)
# 	assert pairs.getPair(token0, token1) == null, 'PAIR EXISTS';
#
# 	# get_bytecode
# 	salt = sha256.encode(token0, token1)
#
# 	pair = new Pair(0, add(bytecode, 32), mload(bytecode), salt)
# 	pair.initialize(token0, token1)
#
# 	S[token0][token1] = pair
# 	S[token1][token0] = pair
# 	all_pairs.append(pair)
#
# 	emit PairCreated(token0, token1, pair, allPairs.length)
#
#
# # @export
# # def create_market(str token_contract, int initial_price, int initial_amount):
# # 	assert initial_price > 0
# # 	assert initial_amount > 0
# #
# # 	# Make sure that what is imported is actually a valid token
# # 	token = importlib.import_module(token_contract)
# # 	assert token_interface.matches(token)
# #
# # 	assert S[token_contract] is None, 'Market already exists!'
# #
# # 	tau_required = initial_amount * initial_price
# #
# # 	currency.transfer_from(ctx.sender, ctx.this, tau_required)
# # 	token.transfer_from(ctx.sender, ctx.this, amount)
# #
# # 	S[token_contract, 'token_liq'] = amount
#
#
