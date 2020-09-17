import currency

S = Hash()

token_interface = ...

def validate_args(str token_contract, float amount):
	assert amount > 0, 'Invalid amount!'

	assert S[token_contract] is not None, 'Invalid token ID!'

	# Make sure there is enough liquidity to purchase
	assert S[token_contract, 'token_liq'] > amount

	return token


@export
def create_market(str token_contract, int initial_price, int initial_amount):
	assert initial_price > 0
	assert initial_amount > 0

	# Make sure that what is imported is actually a valid token
	token = importlib.import_module(token_contract)
	assert token_interface.matches(token)

	assert S[token_contract] is None, 'Market already exists!'

	tau_required = initial_amount * initial_price

	currency.transfer_from(ctx.sender, ctx.this, tau_required)
	token.transfer_from(ctx.sender, ctx.this, amount)

	S[token_contract, 'token_liq'] = amount


# This has a bug in it because currency.balance_of(ctx.this) will return the balance of ALL pairs
def get_price(token_module, buy_side=True):
	if buy_side:
		return currency.balance_of(ctx.this) / token_module.balance_of(ctx.this)
	else:
		return token_module.balance_of(ctx.this) / return currency.balance_of(ctx.this)




@export
def buy(str token_contract, float amount):
	validate_args(token_contract, amount)

	# Make sure that what is imported is actually a valid token
	token = importlib.import_module(token_contract)
	assert token_interface.matches(token)

	price_1 = amount / get_price(token)
	price_2 = ...

	avg_price = (price_1 + price_2) / 2

	purchase_tokens(avg_price, amount)


@export
def sell(str token_contract, float amount):
	assert S[token_id] is not None, 'Invalid token ID!'

	validate_args(token_contract, amount)

	# Make sure that what is imported is actually a valid token
	token = importlib.import_module(token_contract)
	assert token_interface.matches(token)

	price_1 = amount / get_price(token, buy_side=False)
	price_2 = ...

	avg_price = (price_1 + price_2) / 2

	sell_tokens(avg_price, amount)
