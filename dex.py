def dex() :
    I = importlib

    # Enforceable interface
    token_interface = [
        I.Func('transfer', args=('amount', 'to')),
        I.Func('balance_of', args=('account')),
        I.Func('allowance', args=('owner', 'spender')),
        I.Func('approve', args=('amount', 'to')),
        I.Func('transfer_from', args=('amount', 'to', 'main_account')),
    ]

    Pairs = Hash()

    @export
    def get_length_pairs():
        arr = [1,2]
        return len(arr)

    @export
    def create_pair(tau_contract: str, token_contract: str, tau_amount: int, token_amount: int):
        assert token_amount > 0
        assert tau_amount > 0

        # Make sure that what is imported is actually a valid token
        tau = I.import_module(tau_contract)
        assert I.enforce_interface(tau, token_interface), 'Token contract does not meet the required interface'

        token = I.import_module(token_contract)
        assert I.enforce_interface(token, token_interface), 'Token contract does not meet the required interface'

        assert token.name != tau.name
        assert Pairs[token.name] is None, 'Market already exists!'

        # 1 - This contract will own all amounts sent to it
        token.transfer_from(ctx.sender, ctx.this, token_amount)
        tau.transfer_from(ctx.sender, ctx.this, tau_amount)

        # 2 - But we need to somehow track the specific amounts of TAU/TOKEN reserves
        Pairs[tau.name, token.name, 'token_reserve'] = token_amount
        Pairs[tau.name, token.name, 'tau_reserve'] = tau_amount


    def get_price(tau, token, buy_side: bool = True):
        if buy_side:
            return Pairs[tau.name, token.name, 'tau_reserve'] / token.balance_of(ctx.this)
        else:
            return token.balance_of(ctx.this) / Pairs[tau.name, token.name, 'tau_reserve']