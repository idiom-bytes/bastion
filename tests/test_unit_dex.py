from unittest import TestCase
from contracting.client import ContractingClient

import time

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

    def get_reserves(tau_name, token_name):
        return Pairs[tau_name, token_name, 'tau_reserve'], \
               Pairs[tau_name, token_name, 'token_reserve'], \
               Pairs[tau_name, token_name, 'block_ts_last']

    def get_price(tau, token, buy_side = False):
        if buy_side:
            return Pairs[tau.name, token.name, 'tau_reserve'] / token.balance_of(ctx.this)
        else:
            return token.balance_of(ctx.this) / Pairs[tau.name, token.name, 'tau_reserve']

    # Get token modules, validate & return
    def get_interface(tau_contract, token_contract):
        assert Pairs[tau_contract, token_contract] is not None, 'Invalid token ID!'

        # Make sure that what is imported is actually a valid token
        tau = I.import_module(tau_contract)
        assert I.enforce_interface(tau, token_interface), 'Token contract does not meet the required interface'

        token = I.import_module(token_contract)
        assert I.enforce_interface(token, token_interface), 'Token contract does not meet the required interface'

        return tau, token

    # Only one token, and
    # Returns slippage, rates, etc..
    # X*Y=Z
    def get_trade_details(tau, token, tau_out, token_out):
        # Let's calculate slippage
        # And how much you get out from the trade
        tau_reserve = Pairs[tau_contract, token_contract, 'tau_reserve']
        token_reserve = Pairs[tau_contract, token_contract, 'token_reserve']

        lp_total = tau_reserve * token_reserve

        # Calculate new reserve based on what was passed in
        tau_reserve_new = tau_reserve + tau_in if tau_in > 0 else 0
        token_reserve_new = token_reserve + token_in if token_in > 0 else 0

        # Calculate remaining reserve
        tau_reserve_new = lp_total / token_reserve_new if token_in > 0 else tau_reserve_new
        token_reserve_new = lp_total / tau_reserve_new if tau_in > 0 else token_reserve_new

        # Calculate how much will be removed
        tau_out = tau_reserve - tau_reserve_new if token_in > 0 else 0
        token_out = token_reserve - token_reserve_new if tau_in > 0  else 0

        # Finally, calculate the slippage incurred
        tau_slippage = tau_reserve / tau_reserve_new if token_in > 0 else 0
        token_slippage = token_reserve / token_reserve_new  if tau_in > 0 else 0

        return tau_out, token_out, tau_slippage, token_slippage

    # From UniV2Pair.sol
    def update(tau, token, tau_balance, token_balance, tau_reserve_last, token_reserve_last):
        block_ts = time.time()
        time_elapsed = block_ts - Pairs[tau.name, token.name, 'block_ts_last']

        if time_elapsed > 0 and tau_reserve_last != 0 and token_reserve_last != 0 :
            # TODO - Use "Q notation" calculations to make it float-safe
            # I understand that this is supposed to average price over time...
            # But it doesn't seem cumulative (i.e summing time-series information)
            Pairs[tau.name, token.name, 'tau_price_cumulative_last'] = int(Pairs[tau.name, token.name, 'token_reserve'] / Pairs[tau.name, token.name, 'tau_reserve']) * time_elapsed
            Pairs[tau.name, token.name, 'token_price_cumulative_last'] = int(Pairs[tau.name, token.name, 'tau_reserve'] / Pairs[tau.name, token.name, 'token_reserve']) * time_elapsed

        Pairs[tau.name, token.name, 'tau_reserve'] = tau_balance
        Pairs[tau.name, token.name, 'token_reserve'] = token_balance
        Pairs[tau.name, token.name, 'block_ts_last'] = block_ts

        # emit Sync(reserve0, reserve1);

    # .SOL -> Lamden
    # amount0Out -> tau_out
    # amount1Out -> token_out
    # Ported from UniswapV2Pair.sol @ line 159
    # // this low-level function should be called from a contract which performs important safety checks
    # function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external lock {
    def swap(tau_contract:str, token_contract: str, tau_out: float, token_out: float, to: str):

        assert not (tau_out > 0 and token_out > 0), 'Two coin Outputs'
        assert tau_out > 0 or token_out > 0, 'Insufficient Ouput Amount'
        tau, token = get_interface(tau_contract, token_contract)

        tau_reserve = Pairs[tau.name, token.name, 'tau_reserve']
        token_reserve = Pairs[tau.name, token.name, 'token_reserve']

        assert tau_reserve > tau_out and token_reserve > token_out, 'UniswapV2: Inssuficient Liquidity'

        # TODO - A2 - Why is this called BEFORE downstream asserts?
        # TODO - A2 - How is SOL.safe_transfer() != TAU.transfer_from()
        if (tau_out > 0):
            tau.transfer_from(ctx.this, to, tau_out)

        if (token_out > 0):
            token.transfer_from(ctx.this, to, token_out)

        # TODO - B1 - Identify this call from UniV2
        # if (data.length > 0) IUniswapV2Callee(to).uniswapV2Call(msg.sender, amount0Out, amount1Out, data);

        tau_balance = tau.balance_of(this.ctx)
        token_balance = token.balance_of(this.ctx)

        tau_in = tau_balance - (tau_reserve - tau_out) if tau_balance > tau_reserve - tau_out else 0
        token_in = token_balance - (token_reserve - token_out) if token_balance > token_reserve - token_out else 0

        assert tau_in > 0 or token_in > 0, 'UniswapV2: Insufficient Input Amount'

        # TODO - A1/A2 - Deconstruct Curve Adjustment Calculation
        # ... I'm not sure why balances are being multiplied by 1000, then 3...
        # I'm guessing this has something to do with smoothing the balance curve
        tau_balance_adjusted = (tau_balance*1000) - (tau_in*3)
        token_balance_adjusted = (token_balance*1000) - (token_in*3)

        assert tau_balance_adjusted * token_balance_adjusted >= (tau_reserve * token_reserve) * (1000^2), 'UniswapV2: Exception: K'

        # TODO - A1/A2 - Implement update function
        update(tau_balance, token_balance, tau_reserve, token_reserve)

        # TODO - B2 - Event Emitters?
        # emit Swap(msg.sender, amount0In, amount1In, amount0Out, amount1Out, to);

    # Simple getter
    @export
    def get_length_pairs():
        arr = [1,2]
        return len(arr)

    @export
    def token_swap(tau_contract:str, token_contract:str, tau_in: float, token_in: float):
        assert tau_in > 0 or token_in > 0, 'Invalid amount!'
        assert not tau_in > 0 and token_in > 0, 'Swap only accepts one currecy!'
        assert Pairs[tau_contract, token_contract] is not None, 'Invalid token ID!'

        assert Pairs[tau_contract, token_contract, 'tau_reserve'] > 0
        assert Pairs[tau_contract, token_contract, 'token_reserve'] > 0

        tau_reserve_new, token_reserve_new, tau_out, token_out, tau_slippage, token_slippage = get_trade_details()

        tau, token = get_interface(tau_contract, token_contract)
        swap(tau_contract, token_contract, tau_out, token_out)

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

        update(tau.balance_of(ctx.this), token.balance_of(ctx.this), tau_amount, token_amount)

class MyTestCase(TestCase):

    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        self.client.submit(dex, 'dex')

    def test_create_pair(self):
        dex = self.client.get_contract('dex')

        self.assertEqual(dex.get_length_pairs(), 2)