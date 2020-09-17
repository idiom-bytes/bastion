# import currency
#
# def pair():
#     # Convenience
#     I = importlib
#
#     # Storage
#     S = Hash()
#
#     # Enforceable interface
#     token_interface = [
#         I.Func('transfer', args=('amount', 'to')),
#         I.Func('balance_of', args=('account')),
#         I.Func('allowance', args=('owner', 'spender')),
#         I.Func('approve', args=('amount', 'to')),
#         I.Func('transfer_from', args=('amount', 'to', 'main_account')),
#     ]
#
#     def validate_args(str token_contract, float amount):
#         assert amount > 0, 'Invalid amount!'
#
#         assert S[token_contract] is not None, 'Invalid token ID!'
#
#         # Make sure there is enough liquidity to purchase
#         assert S[token_contract, 'token_liq'] > amount
#
#         return token
#
#
#     @export
#     def create_market(str token_contract, int initial_price, int initial_amount):
#         assert initial_price > 0
#         assert initial_amount > 0
#
#         # Make sure that what is imported is actually a valid token
#         token = importlib.import_module(token_contract)
#         assert token_interface.matches(token)
#
#         assert S[token_contract] is None, 'Market already exists!'
#
#         tau_required = initial_amount * initial_price
#
#         currency.transfer_from(ctx.sender, ctx.this, tau_required)
#         token.transfer_from(ctx.sender, ctx.this, amount)
#
#         S[token_contract, 'token_liq'] = amount
#
#
#     # This has a bug in it because currency.balance_of(ctx.this) will return the balance of ALL pairs
#     def get_price(token_module, buy_side=True):
#         if buy_side:
#             return currency.balance_of(ctx.this) / token_module.balance_of(ctx.this)
#         else:
#             return token_module.balance_of(ctx.this) / return currency.balance_of(ctx.this)
