def dex() :
    I = importlib

    Pairs = Hash()
    lamden = Variable()

    # Enforceable interface
    token_interface = [
        I.Func('transfer', args=('amount', 'to')),
        I.Func('balance_of', args=('account')),
        I.Func('allowance', args=('owner', 'spender')),
        I.Func('approve', args=('amount', 'to')),
        I.Func('transfer_from', args=('amount', 'to', 'main_account')),
    ]

    # @construct
    # def seed(lamden_module: object):
    #     lamden.set(lamden_module)

    @export
    def all_pairs_length():
        pair_length =  Pairs.length()
        return pair_length

    # @export
    # def get_price(token_contract: str, buy_side: bool = True):
    #     # Make sure that what is imported is actually a valid token
    #     token = I.import_module(token_contract)
    #     assert I.enforce_interface(token, token_interface), 'Token contract does not meet the required interface'
    #
    #     if buy_side:
    #         return Pairs[currency, token, 'tau_reserve'] / token.balance_of(ctx.this)
    #     else:
    #         return token.balance_of(ctx.this) / Pairs[currency, token, 'tau_reserve']

    @export
    def create_pair(token_contract: str, tau_amount: int, token_amount: int):
        assert token_amount > 0
        assert tau_amount > 0

        # Make sure that what is imported is actually a valid token
        token = I.import_module(token_contract)
        assert I.enforce_interface(token, token_interface), 'Token contract does not meet the required interface'

        assert token.name != tau.name
        assert Pairs[token.name] is None, 'Market already exists!'

        # This contract will own all amounts sent to it
        token.transfer_from(ctx.sender, ctx.this, token_amount)
        tau.transfer_from(ctx.sender, ctx.this, tau_amount)

        # We need to somehow track the specific amounts of TAU/TOKEN reserves
        Pairs[tau.name, token.name, 'token_reserve'] = token_amount
        Pairs[tau.name, token.name, 'tau_reserve'] = tau_amount
