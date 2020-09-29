import math
from unittest import TestCase
from contracting.client import ContractingClient

def tau() :
    balances = Hash(default_value=0)
    token_name = Variable()
    token_symbol = Variable()

    # Cannot set breakpoint in @construct
    @construct
    def seed(s_name:str, s_symbol: str, vk: str, vk_amount: int):
        # Overloading this to mint tokens
        token_name.set(s_name)
        token_symbol.set(s_symbol)
        balances[vk] = vk_amount

    @export
    def token_name():
        return token_name.get()

    @export
    def token_symbol():
        return token_symbol.get()

    @export
    def transfer(amount: float, to: str):
        assert amount > 0, 'Cannot send negative balances!'

        # TODO - A1 - why is this caller, and not signer?
        # if we have a contract calling this, although signed by someone else, this will not work
        sender = ctx.signer

        assert balances[sender] >= amount, 'Not enough coins to send!'

        balances[sender] -= amount
        balances[to] += amount

    @export
    def balance_of(account: str):
        return balances[account]

    @export
    def main_balance_of(main_account: str, account: str):
        return balances[main_account, account]

    @export
    def allowance(owner: str, spender: str):
        return balances[owner, spender]

    @export
    def approve(amount: float, to: str):
        assert amount > 0, 'Cannot send negative balances!'

        sender = ctx.caller
        balances[sender, to] += amount
        return balances[sender, to]

    @export
    def transfer_from(amount: float, from_address: str, to_address: str):
        assert amount > 0, 'Cannot send negative balances!'
        assert balances[from_address] > amount, 'Cannot send amount greater than balance!'

        # TODO - A1 - Trying to understand this currency.py vs. function in general...
        balances[from_address] -= amount
        balances[to_address] += amount

def eth() :
    balances = Hash(default_value=0)
    token_name = Variable()
    token_symbol = Variable()

    # Cannot set breakpoint in @construct
    @construct
    def seed(s_name:str, s_symbol: str, vk: str, vk_amount: int):
        # Overloading this to mint tokens
        token_name.set(s_name)
        token_symbol.set(s_symbol)
        balances[vk] = vk_amount

    @export
    def token_name():
        return token_name.get()

    @export
    def token_symbol():
        return token_symbol.get()

    @export
    def transfer(amount: float, to: str):
        assert amount > 0, 'Cannot send negative balances!'

        # TODO - A1 - why is this caller, and not signer?
        sender = ctx.signer

        assert balances[sender] >= amount, 'Not enough coins to send!'

        balances[sender] -= amount
        balances[to] += amount

    @export
    def balance_of(account: str):
        return balances[account]

    @export
    def main_balance_of(main_account: str, account: str):
        return balances[main_account, account]

    @export
    def allowance(owner: str, spender: str):
        return balances[owner, spender]

    @export
    def approve(amount: float, to: str):
        assert amount > 0, 'Cannot send negative balances!'

        sender = ctx.caller
        balances[sender, to] += amount
        return balances[sender, to]

    @export
    def transfer_from(amount: float, from_address: str, to_address: str):
        assert amount > 0, 'Cannot send negative balances!'
        assert balances[from_address] > amount, 'Cannot send amount greater than balance!'

        # TODO - A1 - Trying to understand this currency.py vs. function in general...
        balances[from_address] -= amount
        balances[to_address] += amount


# TODO - Liquidity pools - mint / burn
# TODO - Reserves (gas savings) vs. Balance
# TODO - KLast
# TODO - Fees
# TODO - Minimum liquidity
def dex() :
    # Illegal use of a builtin
    # import time
    I = importlib

    # Enforceable interface
    token_interface = [
        I.Func('transfer', args=('amount', 'to')),
        I.Func('balance_of', args=('account',))
    ]

    pair_token_interface = [
        I.Func('transfer', args=('amount', 'to')),
        I.Func('balance_of', args=('account',))
    ]

    # BASE PAIR STATE
    # Token
    # token = import_module(token_contract: str)
    # Token Balance
    # balance = _token.balance(address: str)
    # Pair - Rserves
    # tau_reserve = _pairs[tau_contract: str, token-contract: str, 'tau_reserve']
    # token_reserve = _pairs[tau_contract: str, token-contract: str, 'token_reserve']

    # LP TOKENS STATE
    # LP Token totalSupply
    # lp_token_supply = _pairs[tau_contract: str, token_contract: str, 'lp_token_supply']
    # LP Token kLast
    # lp_token_klast = _pairs[tau_contract: str, token_contract: str, 'klast']
    # LP Token balance
    # lp_token_balance = _pairs[tau_contract: str, token_contract: str, 'lp_token_balance', address:str]_
    _pairs = Hash()

    # Contract management variables
    _fee_to = Variable()
    _fee_to_setter = Variable()
    _migrator = Varibale()

    # TODO - Verifiy minimum liquidity
    MINIMUM_LIQUIDITY = 1
    TOKEN_DECIMALS = 18

    # Get token modules, validate & return
    def get_token_interface(tau_contract, token_contract):
        # Make sure that what is imported is actually a valid token
        tau = I.import_module(tau_contract)
        assert I.enforce_interface(tau, token_interface), 'Tau contract does not meet the required interface'

        token = I.import_module(token_contract)
        assert I.enforce_interface(token, token_interface), 'Token contract does not meet the required interface'

        return tau, token

    def get_pair_token_interface(pair_contract):
        # Make sure that what is imported is actually a valid token
        pair = I.import_module(pair_contract)
        assert I.enforce_interface(pair, pair_token_interface), 'Pair Token contract does not meet the required interface'

        return pair

    # TODO - Validate safe_transfer works for TAU + Other tokens
    # Pair Fn
    def safe_transfer(token, to, amount) :
        results = token.transfer(to, amount)
        assert results and isinstance(results, bool) and results == True, 'Transfer Failed'

    # Get zero address
    def zero_address():
        address = '0x'
        for i in range(0,TOKEN_DECIMALS) :
            address += '0'
        return address

    def calculate_trade_details(tau_contract, token_contract, tau_in, token_in):
        # First we need to get tau + token reserve
        tau_reserve = _pairs[tau_contract, token_contract, 'tau_reserve']
        token_reserve = _pairs[tau_contract, token_contract, 'token_reserve']

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
        tau_slippage = (tau_reserve / tau_reserve_new) -1 if token_in > 0 else 0
        token_slippage = (token_reserve / token_reserve_new) -1 if tau_in > 0 else 0

        return tau_out, token_out, tau_slippage, token_slippage

    # From UniV2Pair.sol
    def update(tau, token, tau_balance, token_balance, tau_reserve_last, token_reserve_last):
        # block_ts = time.time()
        # time_elapsed = block_ts - _pairs[tau.name, token.name, 'block_ts_last']

        # if time_elapsed > 0 and tau_reserve_last != 0 and token_reserve_last != 0 :
        #     TODO - Calculate price_cumulative_last
        #     Need time.time() to calculate price_cumulative_last
        #     _pairs[tau.token_name(), token.token_name(), 'tau_price_cumulative_last'] = int(_pairs[tau.name, token.name, 'token_reserve'] / _pairs[tau.name, token.name, 'tau_reserve']) * time_elapsed
        #     _pairs[tau.token_name(), token.token_name(), 'token_price_cumulative_last'] = int(_pairs[tau.name, token.name, 'tau_reserve'] / _pairs[tau.name, token.name, 'token_reserve']) * time_elapsed

        _pairs[tau.token_name(), token.token_name(), 'tau_reserve'] = tau_balance
        _pairs[tau.token_name(), token.token_name(), 'token_reserve'] = token_balance
        # _pairs[tau.token_name(), token.token_name(), 'block_ts_last'] = block_ts

    # TODO - Verify security => Move to lp_token obj
    # Currency/Pair Fn - Internal Interface
    def mint_lp_tokens(tau, token, to_address:str, value: int) :
        # Increase LP Token supply
        lp_token_supply = _pairs[tau.token_name(), token.token_name(), 'lp_token_supply']
        lp_token_supply += value

        # Increase Acct LP Token balance
        lp_token_balance = _pairs[tau.token_name(), token.token_name(), 'lp_token_balance', to_address]
        lp_token_balance = lp_token_balance + value

        # return new supply, and balance
        return _pairs[tau.token_name(), token.token_name(), 'lp_token_supply'], _pairs[tau.token_name(), token.token_name(), 'lp_token_balance', to_address]
        #emit Transfer(address_zero(), to, value)

    # TODO - Verify security => Move to pair/lp_token obj
    # Currency/Pair Fn - Internal Interface
    def burn_lp_tokens(tau, token, from_address: str, value: int) :
        # Decrease LP Token supply
        lp_token_supply = _pairs[tau.token_name(), token.token_name(), 'lp_token_supply']
        lp_token_supply = lp_token_supply - value

        # Decrease Acct LP Token balance
        lp_token_balance = _pairs[tau.token_name(), token.token_name(), 'lp_token_balance', from_address]
        lp_token_balance = lp_token_balance - value

        # return new supply, and balance
        return _pairs[tau.token_name(), token.token_name(), 'lp_token_supply'], _pairs[tau.token_name(), token.token_name(), 'lp_token_balance', from_address]
        # emit Transfer(address_zero(), to, value)

    # TODO - Validate
    # DONE - PORTED + REVIEWED
    # UniswapV2Pai.sol => _mintFee()
    def mint_fee(tau, token, tau_reserve, token_reserve):
        lp_token_supply = _pairs[tau.token_name(), token.token_name(), 'lp_token_supply']

        fee_on = _fee_to != zero_address() # make sure we're not burning the fee?
        kLast = _pairs[tau.token_name(), token.token_name(), 'kLast'] # "gas savings"
        if(fee_on) :
            if(kLast != 0) :
                rootK = math.sqrt(tau_reserve * token_reserve)
                rootKLast = math.sqrt(kLast)
                if(rootK > rootKLast) :
                    numerator = lp_token_supply * (rootK - rootKLast)
                    denominator = (rootK * 5) + rootKLast
                    liquidity = numerator / denominator
                    if(liquidity > 0):
                        mint_lp_tokens(tau, token, _fee_to, liquidity)
        elif(kLast != 0) :
            _pairs[tau.token_name(), token.token_name(), 'kLast'] = 0

        return fee_on

    # TODO - VALIDATE
    # DONE -> PORTED + REVIEWED
    # UniswapV2Pai.sol => mint()
    # This low-level function should be called from a contract which performs important safety checks
    def mint_liquidity(tau, token, to):
        # 1 - State reserves (current state)
        tau_reserve, token_reserve = get_reserves(tau.token_name, token.token_name) # "gas savings"
        # 2 - Token reserves (new state)
        tau_balance = tau.balance_of(ctx.this)
        token_balance = token.balance_of(ctx.this)
        # 3 - How many tokens were added
        tau_amount = tau_balance - tau_reserve
        token_amount = token_balance - token_reserve

        # We update how to handle fees, before updating liquidity
        fee_on = mint_fee(tau, token, tau_reserve, token_reserve)
        lp_token_supply = _pairs[tau.token_name(), token.token_name(), 'lp_token_supply'] # "gas savings"
        if(lp_token_supply == 0 ) :
            # TODO - Migrator logic
            # Initial liquidity = SeedLiquidity - MinimumLiquidity-
            liquidity = math.sqrt(tau_amount * token_amount) - MINIMUM_LIQUIDITY
            mint_lp_tokens(tau, token, zero_address(), MINIMUM_LIQUIDITY) # permanently lock the first MINIMUM_LIQUIDITY tokens
        else :
            # Get new liquidity
            liquidity = min(
                ( tau_amount * lp_token_supply ) / tau_reserve,
                ( token_amount * lp_token_supply ) / token_reserve
            )

        # Assign LP Tokens to provider
        assert liquidity > 0, 'Insufficient liquidity minted'
        mint_lp_tokens(tau, token, to, liquidity)

        # Update Pair internal state
        update(tau, token, tau_balance, token_balance, tau_reserve, token_reserve)
        if(fee_on) :
            # tau_reserve & token_reserve are up-to-date
            # Update kLast to calculate fees
            _pairs[tau.tau.token_name(), token.token_name(), 'kLast'] = tau_reserve * token_reserve

        #emit Mint(ctx.signer, tau_amount, token_amount)
        return ctx.signer, tau_amount, token_amount

    # Used when liquidity is removed
    # TODO - Finish Implementation + Validate
    # UniswapV2Pai.sol => burn()
    # This low-level function should be called from a contract which performs important safety checks
    def burn_liquidity(tau, token, to_address):
        tau_reserve, token_reserve = get_reserves(tau.token_name, token.token_name) # gas savings
        tau_balance = tau.balance_of(ctx.this)
        token_balance = token.balance_of(ctx.this)
        lp_token_liquidity = _pairs[tau.tau.token_name(), token.token_name(), 'lp_token_balance', ctx.this]

        # We update how to handle fees, before updating liquidity
        fee_on = mint_fee(tau, token, tau_reserve, token_reserve)
        lp_token_supply = _pairs[tau.token_name(), token.token_name(), 'lp_token_supply']
        tau_amount = (lp_token_liquidity * tau_balance) / lp_token_supply # using balances ensures pro-rata distribution
        token_amount = (lp_token_liquidity * token_balance) / lp_token_supply # using balances ensures pro-rata distribution
        assert tau_amount > 0 and token_amount > 0, 'Insufficient liquidity burned'

        # destroy lp tokens + return tokens
        burn_lp_tokens(tau, token, ctx.this, lp_token_liquidity)
        safe_transfer(tau, to_address, tau_amount)
        safe_transfer(token, to_address, token_amount)

        # Get new Dex balance
        tau_balance = tau.balance_of(ctx.this)
        token_balance = token.balance_of(ctx.this)

        # Update Pair internal state
        update(tau, token, tau_balance, token_balance, tau_reserve, token_reserve)
        if(fee_on):
            # Update kLast to calculate fees
            _pairs[tau.tau.token_name(), token.token_name(), 'kLast'] = tau_reserve * token_reserve

        #emit Burn(ctx.signer, tau_amount, token_amount, to_address)
        return ctx.signer, tau_amount, token_amount, to_address

    # Route01 Fn
    # UniswapV2Router01.sol => addLiquidity()
    def _add_liquidity(tau, token, tau_desired, token_desired, tau_min, token_min):

        assert tau.token_name() != token.token_name(), 'Tokens must be unique'
        if( _pairs[tau.token_name(), token.token_name()] is None ):
            create_pair(tau.token_name, token.token_name)

        tau_amount, token_amount = 0,0
        tau_reserve, token_reserve = get_reserves(tau.token_name, token.token_name)  # gas savings
        if( tau_reserve == 0 and token_reserve == 0 ) :
            tau_amount, token_amount = tau_desired, token_desired
        else :
            token_optimal = quote(tau_desired, tau_reserve, token_reserve)
            if(token_optimal <= token_desired) :
                assert token_optimal >= token_min, 'Insufficient token amount'
                tau_amount, token_amount = tau_desired, token_optimal
            else :
                tau_optimal = quote(token_desired, token_reserve, tau_reserve)
                assert tau_optimal <= tau_desired, 'Insufficient desired tau'
                assert tau_optimal >= tau_min, 'Insufficient tau amount'
                tau_amount, token_amount = tau_optimal, token_desired

        return tau_amount, token_amount

    # Route01 Fn
    # UniswapV2Router01.sol => removeLiquidity()
    def _remove_liquidity(tau, token, liquidity, tau_min, token_min, to_address):
        assert tau.token_name() != token.token_name(), 'Tokens must be unique'

        _pair[tau.token_name(), token.token_name()].transfer_from(ctx.caller, ctx.this, liquidity)
        tau_amount, token_amount = burn_liquidity(tau, token, to_address)

        token_sorted = sort_tokens(tau, token)
        tau_amount, token_amount = tau_amount, token_amount if tau == token_sorted else token_amount, tau_amount

        assert tau_amount > tau_min, 'Insufficient Tau amount'
        assert token_amount > token_min, 'Insufficient Token amount'

        return tau_amount, token_amount

    # Pair Fn
    # UniswapV2Pair.sol => swap()
    # This low-level function should be called from a contract which performs important safety checks
    # function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external lock {
    def swap(tau, token, tau_out, token_out, to):
        assert not (tau_out > 0 and token_out > 0), 'Only one Coin Out allowed'
        assert tau_out > 0 or token_out > 0, 'Insufficient Ouput Amount'

        tau_reserve = _pairs[tau.token_name(), token.token_name(), 'tau_reserve']
        token_reserve = _pairs[tau.token_name(), token.token_name(), 'token_reserve']

        assert tau_reserve > tau_out and token_reserve > token_out, 'UniswapV2: Inssuficient Liquidity'

        # TODO - A2 - Why is this called BEFORE downstream asserts?
        # TODO - A2 - How is SOL.safe_transfer() != TAU.transfer_from()
        if tau_out > 0 :
            tau.transfer_from(tau_out, ctx.this, to)
        if token_out > 0 :
            token.transfer_from(token_out, ctx.this, to)

        # TODO - B1 - Identify this call from UniV2
        # if (data.length > 0) IUniswapV2Callee(to).uniswapV2Call(msg.sender, amount0Out, amount1Out, data);

        tau_balance = tau.balance_of(ctx.this)
        token_balance = token.balance_of(ctx.this)

        # TODO - A1/A2 - Deconstruct Curve Adjustment Calculation
        # tau_in = tau_balance - (tau_reserve - tau_out) if tau_balance > tau_reserve - tau_out else 0
        # token_in = token_balance - (token_reserve - token_out) if token_balance > token_reserve - token_out else 0
        #
        # assert tau_in > 0 or token_in > 0, 'UniswapV2: Insufficient Input Amount'
        #
        # ... I'm not sure why balances are being multiplied by 1000, then 3, then by 1000^2
        # I'm guessing this has something to do with smoothing the balance curve
        # tau_balance_adjusted = (tau_balance*1000) - (tau_in*3)
        # token_balance_adjusted = (token_balance*1000) - (token_in*3)
        #
        # assert tau_balance_adjusted * token_balance_adjusted >= (tau_reserve * token_reserve) * (1000^2), 'UniswapV2: Exception: K'

        # TODO - A1/A2 - Implement update function
        update(tau, token, tau_balance, token_balance, tau_reserve, token_reserve)

        # TODO - B2 - Event Emitters?
        # emit Swap(msg.sender, amount0In, amount1In, amount0Out, amount1Out, to);

    @construct
    def seed(fee_to_setter:str):
        _pairs['count'] = 0
        _fee_to_setter = fee_to_setter

    @export
    # Number of _pairs created
    def get_length__pairs():
        return _pairs['count']

    # Contract management Fns
    @export
    def set_fee_to(fee_to_address: str):
        assert ctx.caller == _fee_to_setter, 'Forbidden'
        _fee_to_setter = fee_to_address

    @export
    def set_migrator(migrator_address: str):
        assert ctx.caller == _fee_to_setter, 'Forbidden'
        _migrator = migrator_address

    @export
    def set_fee_to_setter(fee_to_setter: str):
        assert ctx.caller == _fee_to_setter, 'Forbidden'
        _fee_to_setter = fee_to_setter

    @export
    # Returns the total reserves from each tau/token
    def get_reserves(tau_contract:str, token_contract:str):
        return _pairs[tau_contract, token_contract, 'tau_reserve'], \
                _pairs[tau_contract, token_contract, 'token_reserve']

    @export
    # Pass contracts + tokens_in, get: tokens_out, slippage
    def get_trade_details(tau_contract: str, token_contract: str, tau_in: int, token_in: int):
        return calculate_trade_details(tau_contract, token_contract, tau_in, token_in)

    @export
    # Route01 Fn
    # Frankenstein calculate_trade_details() + UniswapV2Router1.sol => swap()
    def token_swap(tau_contract: str, token_contract: str, tau_in: float, token_in: float, to: str):
        assert tau_in > 0 or token_in > 0, 'Invalid amount!'
        assert not (tau_in > 0 and token_in > 0), 'Swap only accepts one currecy!'

        assert not _pairs[tau_contract, token_contract] is None, 'Invalid token ID!'
        assert _pairs[tau_contract, token_contract, 'tau_reserve'] > 0
        assert _pairs[tau_contract, token_contract, 'token_reserve'] > 0

        tau, token = get_token_interface(tau_contract, token_contract)

        # 1 - Calculate trade outcome
        tau_out, token_out, tau_slippage, token_slippage = calculate_trade_details(
            tau_contract,
            token_contract,
            tau_in,
            token_in
        )

        # 2 - Transfer in tokens
        if tau_in > 0 : tau.transfer(tau_in, ctx.this)
        if token_in > 0 : token.transfer(token_in, ctx.this)

        # 3 - Swap/transfer out tokens + Update
        swap(tau, token, tau_out, token_out, to)

    # Route01 Fn
    # Pair must exist before liquidity can be added
    @export
    def add_liquidity(tau_contract: str, token_contract: str, tau_in: int, token_in: int):
        assert token_in > 0
        assert tau_in > 0

        # Make sure that what is imported is actually a valid token
        tau, token = get_token_interface(tau_contract, token_contract)

        assert tau_contract != token_contract
        assert not _pairs[tau_contract, token_contract] is None, 'Market does not exist!'

        # 1 - This contract will own all amounts sent to it
        tau.transfer(tau_in, ctx.this)
        token.transfer(token_in, ctx.this)

        # Track liquidity provided by signer
        # TODO - If we care about "% pool" This needs to remain updated as market swings along X,Y
        if _pairs[tau_contract, token_contract, ctx.signer] is None :
            _pairs[tau_contract, token_contract, 'tau_liquidity', ctx.signer] = tau_in
            _pairs[tau_contract, token_contract, 'token_liquidity', ctx.signer] = token_in
        else :
            _pairs[tau_contract, token_contract, 'tau_liquidity', ctx.signer] += tau_in
            _pairs[tau_contract, token_contract, 'token_liquidity', ctx.signer] += token_in

        # I'm assuming registry of [ctx.this,ctx.investor,amount] is done via LP
        update(
            tau,
            token,
            tau.balance_of(ctx.this),
            token.balance_of(ctx.this),
            _pairs[tau.token_name(), token.token_name(), 'tau_reserve'],
            _pairs[tau.token_name(), token.token_name(), 'token_reserve']
        )

    # Factory Fn
    # Create pair before doing anything else
    @export
    def create_pair(tau_contract: str, token_contract: str, tau_in: int, token_in: int):
        # Make sure that what is imported is actually a valid token
        tau, token = get_token_interface(tau_contract, token_contract)

        assert tau_contract != token_contract
        assert _pairs[tau_contract, token_contract] is None, 'Market already exists!'

        # 1 - Create the pair
        _pairs[tau_contract, token_contract] = token_contract
        _pairs['count'] += 1

        # 2 - Adds liquidity if provided
        if (not tau_in is None and tau_in > 0) and (not token_in is None and token_in > 0) :
            add_liquidity(tau_contract, token_contract, tau_in, token_in)


class MyTestCase(TestCase):

    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        # Currently mocking Lamdem functionality w/ inline tokens
        self.client.submit(tau, 'lamden', constructor_args={
            's_name': 'lamden',
            's_symbol': 'TAU',
            'vk': 'actor1',
            'vk_amount': 15
        })

        self.client.submit(eth, 'ethereum', constructor_args={
            's_name': 'ethereum',
            's_symbol': 'ETH',
            'vk': 'actor1',
            'vk_amount': 15
        })

        self.client.submit(dex, 'dex')


    def change_signer(self, name):
        self.client.signer = name

        self.lamden = self.client.get_contract('lamden')
        self.ethereum = self.client.get_contract('ethereum')
        self.dex = self.client.get_contract('dex')

    # Unit Test designed around
    # UniV2
    # X+Y=Z AMMs - https://ethresear.ch/t/improving-front-running-resistance-of-x-y-k-market-makers/1281
    def test_1_token_interfaces(self):
        self.change_signer('actor1')

        # get balances
        self.assertEqual(self.lamden.token_name(), 'lamden')
        self.assertEqual(self.lamden.token_symbol(), 'TAU')
        self.assertEqual(self.lamden.quick_read('balances', 'actor1'), 15)
        self.assertEqual(self.lamden.balance_of(account='actor1'), 15)

        self.assertEqual(self.ethereum.token_name(), 'ethereum')
        self.assertEqual(self.ethereum.token_symbol(), 'ETH')
        self.assertEqual(self.ethereum.quick_read('balances', 'actor1'), 15)
        self.assertEqual(self.ethereum.balance_of(account = 'actor1'), 15)

    def test_2_dex_create_pair(self):
        self.change_signer('actor1')

        n__pairs_before = self.dex.get_length__pairs()

        # Optionally => Pass in tau_in and token_in
        self.dex.create_pair(
            tau_contract = 'lamden',
            token_contract = 'ethereum',
            tau_in=10,
            token_in=10
        )

        # Verify _pairs increased
        n__pairs_after = self.dex.get_length__pairs()
        assert n__pairs_after > n__pairs_before


        # The dex should now own 10 of each
        self.assertEqual(self.lamden.balance_of(account='actor1'), 5)
        self.assertEqual(self.lamden.balance_of(account='dex'), 10)

        self.assertEqual(self.ethereum.balance_of(account='actor1'), 5)
        self.assertEqual(self.ethereum.balance_of(account='dex'), 10)

        # Verify reserves are in place
        tau_reserve, token_reserve = self.dex.get_reserves(
            tau_contract = 'lamden',
            token_contract = 'ethereum'
        )

        self.assertEqual(tau_reserve, 10)
        self.assertEqual(token_reserve, 10)

    def test_3_dex_review_trade(self):
        self.change_signer('actor1')

        # CREATE MARKET + ADD LIQUIDITY
        # Create pair (this will be owned by the dex)
        self.dex.create_pair(
            tau_contract='lamden',
            token_contract='ethereum'
        )

        # Add liquidity
        self.dex.add_liquidity(
            tau_contract='lamden',
            token_contract='ethereum',
            tau_in=10,
            token_in=10
        )

        # TRADE NUMBER 1 - Check trade details
        # Miner spends one unit of A: (11, 9.090909), gets 0.909091 units of B
        tau_out, token_out, tau_slippage, token_slippage = self.dex.get_trade_details(
            tau_contract='lamden',
            token_contract='ethereum',
            tau_in=1,
            token_in=0
        )

        # Review trade details are correct
        assert tau_out == 0
        assert round(token_out, 6) == 0.909091
        assert round(token_slippage, 2) * 100 == 10.00

    def test_4_dex_swap(self):
        self.change_signer('actor1')

        # Distribute currencies to other actors
        self.lamden.transfer(amount = 1, to = 'miner')
        self.lamden.transfer(amount = 1, to = 'buyer')

        # CREATE MARKET + ADD LIQUIDITY
        # Create pair (this will be owned by the dex)
        self.dex.create_pair(
            tau_contract='lamden',
            token_contract='ethereum'
        )

        # Add liquidity
        self.dex.add_liquidity(
            tau_contract='lamden',
            token_contract='ethereum',
            tau_in = 10,
            token_in = 10
        )

        # TRADE NUMBER 1 - MINER
        # Miner spends one unit of A: (11, 9.090909), gets 0.909091 units of B
        self.change_signer('miner')
        self.dex.token_swap(
            tau_contract = 'lamden',
            token_contract = 'ethereum',
            tau_in = 1,
            token_in = 0,
            to = 'miner'
        )

        # Validate Balances + AMM Reserves Post-Swap
        miner_balance_tau = self.lamden.balance_of(account='miner')
        self.assertEqual(miner_balance_tau, 0)
        miner_balance_eth = round(float(str(self.ethereum.balance_of(account='miner'))),6)
        self.assertEqual(miner_balance_eth, 0.909091)

        dex_balance_tau = self.lamden.balance_of(account='dex')
        self.assertEqual(dex_balance_tau, 11)
        dex_balance_eth = round(float(str(self.ethereum.balance_of(account='dex'))), 6)
        self.assertEqual(dex_balance_eth, 9.090909)

        # Get remaining reserves
        tau_reserve, token_reserve = self.dex.get_reserves(
            tau_contract = 'lamden',
            token_contract = 'ethereum'
        )

        tau_reserve = round(float(str(tau_reserve)), 2)
        self.assertEqual(tau_reserve, 11.0)
        token_reserve = round(float(str(token_reserve)), 6)
        self.assertEqual(token_reserve, 9.090909)


        # TRADE NUMBER 2 - BUYER
        self.change_signer('buyer')

        self.dex.token_swap(
            tau_contract = 'lamden',
            token_contract = 'ethereum',
            tau_in = 1,
            token_in = 0,
            to = 'buyer'
        )

        # Validate Balances + AMM Reserves Post-Swap
        buyer_balance_tau = self.lamden.balance_of(account='buyer')
        self.assertEqual(buyer_balance_tau, 0)
        buyer_balance_eth = round(float(str(self.ethereum.balance_of(account='buyer'))),6)
        self.assertEqual(buyer_balance_eth, 0.757576)

        dex_balance_tau = self.lamden.balance_of(account='dex')
        self.assertEqual(dex_balance_tau, 12)
        dex_balance_eth = round(float(str(self.ethereum.balance_of(account='dex'))), 6)
        self.assertEqual(dex_balance_eth, 8.333333)

        # Get remaining reserves
        tau_reserve, token_reserve = self.dex.get_reserves(
            tau_contract = 'lamden',
            token_contract = 'ethereum'
        )

        tau_reserve = round(float(str(tau_reserve)), 2)
        self.assertEqual(tau_reserve, 12.0)
        token_reserve = round(float(str(token_reserve)), 6)
        self.assertEqual(token_reserve, 8.333333)


        # TRADE NUMBER 3 - MINER
        self.change_signer('miner')

        self.dex.token_swap(
            tau_contract='lamden',
            token_contract='ethereum',
            tau_in=0,
            token_in=0.757576,
            to='miner'
        )

        # Validate Balances + AMM Reserves Post-Swap
        miner_balance_tau = round(float(str(self.lamden.balance_of(account='miner'))), 2)
        self.assertEqual(miner_balance_tau, 1.0)
        miner_balance_eth = round(float(str(self.ethereum.balance_of(account='miner'))), 6)
        self.assertEqual(miner_balance_eth, 0.151515)

        dex_balance_tau = round(float(str(self.lamden.balance_of(account='dex'))),2)
        self.assertEqual(dex_balance_tau, 11.0)
        dex_balance_eth = round(float(str(self.ethereum.balance_of(account='dex'))), 6)
        self.assertEqual(dex_balance_eth, 9.090909)

        # Get remaining reserves
        tau_reserve, token_reserve = self.dex.get_reserves(
            tau_contract='lamden',
            token_contract='ethereum'
        )

        tau_reserve = round(float(str(tau_reserve)), 2)
        self.assertEqual(tau_reserve, 11.0)
        token_reserve = round(float(str(token_reserve)), 6)
        self.assertEqual(token_reserve, 9.090909)
