from unittest import TestCase
from contracting.client import ContractingClient
from contracting.stdlib.bridge.decimal import ContractingDecimal

def tau():
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
        sender = ctx.caller

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

def eth():
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
        sender = ctx.caller

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

def dex_pairs():
    I = importlib

    # Enforceable interface
    token_interface = [
        I.Func('transfer', args=('amount', 'to')),
        I.Func('balance_of', args=('account',))
    ]

    dex_interface = [
        I.Func('fee_to', args=())
    ]

    # LP Balance
    # balance = balance(tau_contract: str, token_contract: str, address: str)
    # Pair - Rserves
    # tau_reserve = pairs[tau_contract: str, token-contract: str, 'tau_reserve']
    # token_reserve = pairs[tau_contract: str, token-contract: str, 'token_reserve']

    # LP TOKENS STATE
    # LP Token totalSupply
    # lp_token_supply = pairs[tau_contract: str, token_contract: str, 'lp_token_supply']
    # LP Token kLast
    # lp_token_klast = pairs[tau_contract: str, token_contract: str, 'klast']
    # LP Token balance
    # lp_token_balance = pairs[tau_contract: str, token_contract: str, 'lp_token_balance', address:str]_
    owner = Variable()
    pairs = Hash()

    # TODO - Verifiy minimum liquidity
    MINIMUM_LIQUIDITY = pow(10,3)
    TOKEN_DECIMALS = 18

    # returns ContractingDecimal
    def expand_to_token_decimals(amount):
        return (amount / pow(10,TOKEN_DECIMALS)) * 1.0 # turn it into contracting decimal

    # returns float
    # babylonian method(https://en.wikipedia.org/wiki/Methods_of_computing_square_roots)
    # Validated with sqrt of: 2,4,6,9
    def sqrt(y) :
        z = None
        if (y > 3) :
            z = y
            x = y / 2 + 1
            while (x < z):
                z = x
                x = (y / x + x) / 2
        elif (y != 0) :
            z = 1

        return z * 1.0 # turn it into contracting decimal

    def get_dex_interface(dex_contract):
        dex = I.import_module(dex_contract)
        # assert I.enforce_interface(dex, dex_interface), 'Dex contract does not meet the required interface'

        return dex

    # Get token modules, validate & return
    def get_token_interface(tau_contract, token_contract):
        # Make sure that what is imported is actually a valid token
        tau = I.import_module(tau_contract)
        assert I.enforce_interface(tau, token_interface), 'Tau contract does not meet the required interface'

        token = I.import_module(token_contract)
        assert I.enforce_interface(token, token_interface), 'Token contract does not meet the required interface'

        return tau, token

    # TODO - A2 - Implement Jeff's "Valid Hex Address"
    # Get zero address
    def zero_address():
        return '0'

    # def calculate_trade_details(tau_contract, token_contract, tau_in, token_in):
    #     # First we need to get tau + token reserve
    #     tau_reserve = pairs[tau_contract, token_contract, 'tau_reserve']
    #     token_reserve = pairs[tau_contract, token_contract, 'token_reserve']
    #
    #     lp_total = tau_reserve * token_reserve
    #
    #     # Calculate new reserve based on what was passed in
    #     tau_reserve_new = tau_reserve + tau_in if tau_in > 0 else 0
    #     token_reserve_new = token_reserve + token_in if token_in > 0 else 0
    #
    #     # Calculate remaining reserve
    #     tau_reserve_new = lp_total / token_reserve_new if token_in > 0 else tau_reserve_new
    #     token_reserve_new = lp_total / tau_reserve_new if tau_in > 0 else token_reserve_new
    #
    #     # Calculate how much will be removed
    #     tau_out = tau_reserve - tau_reserve_new if token_in > 0 else 0
    #     token_out = token_reserve - token_reserve_new if tau_in > 0  else 0
    #
    #     # Finally, calculate the slippage incurred
    #     tau_slippage = (tau_reserve / tau_reserve_new) -1 if token_in > 0 else 0
    #     token_slippage = (token_reserve / token_reserve_new) -1 if tau_in > 0 else 0
    #
    #     return tau_out, token_out, tau_slippage, token_slippage

    # From UniV2Pair.sol
    def update(tau, token, pair_tau_balance, pair_token_balance):
        pairs[tau.token_name(), 'balance'] = tau.balance_of(ctx.this)
        pairs[token.token_name(), 'balance'] = token.balance_of(ctx.this)

        pairs[tau.token_name(), token.token_name(), 'tau_reserve'] = pair_tau_balance
        pairs[tau.token_name(), token.token_name(), 'token_reserve'] = pair_token_balance

    # TODO - A1 - VALIDATE IMPLEMENTATION
    # Currency/Pair Fn - Internal Interface
    def mint_lp_tokens(tau, token, to_address, amount) :
        assert not to_address is None, 'Invalid Address {}'.format(to_address)
        assert isinstance(to_address, str), 'Invalid type {}'.format(to_address)

        # Increase LP Token supply
        pairs[tau.token_name(), token.token_name(), 'lp_token_supply'] += amount

        # Increase Acct LP Token balance
        lp_token_balance = pairs[tau.token_name(), token.token_name(), 'lp_token_balance', to_address]
        pairs[tau.token_name(), token.token_name(), 'lp_token_balance', to_address] = lp_token_balance + amount if not lp_token_balance is None else amount

        # return new supply, and balance
        #emit Transfer(address_zero(), to, amount)
        return zero_address(), to_address, amount

    # TODO - A1 - VALIDATE IMPLEMENTATION/SECURITY
    # Currency/Pair Fn - Internal Interface
    def burn_lp_tokens(tau, token, from_address, amount) :
        # Decrease LP Token supply
        pairs[tau.token_name(), token.token_name(), 'lp_token_supply'] -= amount

        # Decrease Acct LP Token balance
        lp_token_balance = pairs[tau.token_name(), token.token_name(), 'lp_token_balance', from_address]
        pairs[tau.token_name(), token.token_name(), 'lp_token_balance', from_address] = lp_token_balance - amount

        # return new supply, and balance
        # emit Transfer(address_zero(), to, amount)
        return pairs[tau.token_name(), token.token_name(), 'lp_token_supply'], pairs[tau.token_name(), token.token_name(), 'lp_token_balance', from_address]

    # TODO - A1 - VALIDATE IMPLEMENTATION/SECURITY
    # DONE - PORTED + REVIEWED
    # UniswapV2Pai.sol => _mintFee()
    def mint_fee(dex, tau, token, tau_reserve, token_reserve):
        lp_token_supply = pairs[tau.token_name(), token.token_name(), 'lp_token_supply']

        fee_to = dex.fee_to()
        fee_on = fee_to != zero_address() # make sure we're not burning the fee?
        kLast = pairs[tau.token_name(), token.token_name(), 'kLast'] # "gas savings"
        if(fee_on) :
            if(kLast != 0) :
                rootK = sqrt(tau_reserve * token_reserve)
                rootKLast = sqrt(kLast)
                if(rootK > rootKLast) :
                    numerator = lp_token_supply * (rootK - rootKLast)
                    denominator = (rootK * 5) + rootKLast
                    liquidity = numerator / denominator
                    if(liquidity > 0):
                        mint_lp_tokens(tau, token, fee_to, liquidity)
        elif(kLast != 0) :
            pairs[tau.token_name(), token.token_name(), 'kLast'] = 0

        return fee_on, fee_to

    @construct
    def seed(owner_address: str):
        owner.set(owner_address)
        pairs['count'] = 0

    @export
    def pair(tau_contract: str, token_contract: str):
        return pairs[tau_contract, token_contract]

    @export
    # Number of pairs created
    def length_pairs():
        return pairs['count']

    @export
    def pair_address(tau_contract: str, token_contract: str):
        assert not pairs[tau_contract, token_contract] is None, 'Invalid pair'
        return pairs[tau_contract, token_contract, 'pair_address']

    @export
    def total_supply(tau_contract:str, token_contract:str):
        assert not pairs[tau_contract, token_contract] is None, 'Invalid pair'
        return pairs[tau_contract, token_contract, 'lp_token_supply']

    @export
    def initialize(tau_contract:str, token_contract:str):
        assert tau_contract != token_contract
        assert ctx.caller == owner.get(), 'LamDexPairs: FORBIDDEN'

        # Pair Balances
        pairs[tau_contract, token_contract] = ['pair_address', 'tau_reserve', 'token_reserve', 'lp_token_supply', 'kLast', 'lp_token_balance']

        pair_address = hashlib.sha256(tau_contract + token_contract)
        pairs[tau_contract, token_contract, 'pair_address'] = pair_address
        pairs[tau_contract, token_contract, 'tau_reserve'] = 0
        pairs[tau_contract, token_contract, 'token_reserve'] = 0
        pairs[tau_contract, token_contract, 'lp_token_supply'] = 0
        pairs[tau_contract, token_contract, 'lp_token_balance'] = {}
        pairs[tau_contract, token_contract, 'kLast'] = 0
        pairs['count'] += 1

        # Token Balances
        tau, token = get_token_interface(tau_contract, token_contract)

        if pairs[tau_contract, 'balance'] is None :
            pairs[tau_contract, 'balance'] = tau.balance_of(ctx.this)

        if pairs[token_contract, 'balance'] is None :
            pairs[token_contract, 'balance'] = token.balance_of(ctx.this)

    @export
    def pair_address(tau_contract:str, token_contract:str):
        assert not pairs[tau_contract, token_contract] is None, 'Invalid pair'
        return pairs[tau_contract, token_contract, 'pair_address']

    @export
    # Returns the total reserves from each tau/token
    def get_pair_reserves(tau_contract:str, token_contract:str):
        return pairs[tau_contract, token_contract, 'tau_reserve'], \
                pairs[tau_contract, token_contract, 'token_reserve']

    @export
    def balance_of(tau_contract:str, token_contract:str, account:str):
        assert not pairs[tau_contract, token_contract] is None, 'Invalid pair'
        return pairs[tau_contract, token_contract, 'lp_token_balance', account]

    @export
    def transfer(tau_contract:str, token_contract:str, amount:int, to:str):
        assert not pairs[tau_contract, token_contract] is None, 'Invalid pair'
        assert amount > 0, 'Cannot send negative balances!'

        sender = ctx.caller
        assert not pairs[tau_contract, token_contract, 'lp_token_balance', sender] is None, 'Invalid sender'
        assert pairs[tau_contract, token_contract, 'lp_token_balance', sender] >= amount, 'Not enough coins to send!'

        pairs[tau_contract, token_contract, 'lp_token_balance', sender] -= amount

        to_amount = pairs[tau_contract, token_contract, 'lp_token_balance', to]
        pairs[tau_contract, token_contract, 'lp_token_balance', to] = amount + to_amount if not to_amount is None else amount

    # @export
    # # Pass contracts + tokens_in, get: tokens_out, slippage
    # def get_trade_details(tau_contract: str, token_contract: str, tau_in: int, token_in: int):
    #     return calculate_trade_details(tau_contract, token_contract, tau_in, token_in)

    # TODO - A1 - VALIDATE IMPLEMENTATION
    # UniswapV2Pair.sol => mint()
    # This low-level function should be called from a contract which performs important safety checks
    @export
    def mint_liquidity(dex_contract:str, tau_contract:str, token_contract: str, to_address: str):
        # Make sure that what is imported is actually a valid token
        tau, token = get_token_interface(tau_contract, token_contract)
        assert tau_contract != token_contract

        dex = get_dex_interface(dex_contract)
        assert not dex is None, 'Dex needs to be valid'

        # 1 - Last pair reserves
        tau_reserve, token_reserve = get_pair_reserves(tau_contract=tau_contract,token_contract=token_contract) # "gas savings"

        # 2 - Last total balances
        last_total_tau_balance = pairs[tau_contract, 'balance']
        last_total_token_balance = pairs[token_contract, 'balance']

        # New total balances - token.balance()
        new_total_tau_balance = tau.balance_of(ctx.this)
        new_total_token_balance = token.balance_of(ctx.this)

        # Amount delta
        tau_amount = new_total_tau_balance - last_total_tau_balance
        token_amount = new_total_token_balance - last_total_token_balance

        assert tau_amount > 0 and token_amount > 0, 'Invalid token amount'

        # TODO - fee_on
        liquidity = None
        fee_on = mint_fee(dex, tau, token, tau_reserve, token_reserve)
        lp_token_supply = pairs[tau.token_name(), token.token_name(), 'lp_token_supply'] # "gas savings"
        if(lp_token_supply == 0 ) :
            # TODO - A4 - Migrator logic
            # Initial liquidity = SeedLiquidity - MinimumLiquidity
            liquidity = sqrt(tau_amount * token_amount) - expand_to_token_decimals(MINIMUM_LIQUIDITY)
            # permanently lock the first MINIMUM_LIQUIDITY tokens
            mint_lp_tokens(tau, token, zero_address(), expand_to_token_decimals(MINIMUM_LIQUIDITY))
        else :
            # Get new liquidity
            liquidity = min(
                ( tau_amount * lp_token_supply ) / tau_reserve,
                ( token_amount * lp_token_supply ) / token_reserve
            )

        # Assign LP Tokens to provider
        assert liquidity > 0, 'Insufficient liquidity minted'
        mint_lp_tokens(tau, token, to_address, liquidity)

        new_tau_reserve = tau_reserve + tau_amount
        new_token_reserve = token_reserve + token_amount
        # Update Pair internal state
        update(
            tau,
            token,
            new_tau_reserve,
            new_token_reserve
        )

        if(fee_on) :
            # Update kLast to calculate fees
            pairs[tau_contract, token_contract, 'kLast'] = new_tau_reserve * new_token_reserve

        #emit Mint(ctx.signer, tau_amount, token_amount)
        return to_address, tau_amount, token_amount


    # TODO - A1 - Finish Implementation + Validate
    # UniswapV2Pai.sol => burn()
    # This low-level function should be called from a contract which performs important safety checks
    @export
    def burn_liquidity(dex_contract: str, tau_contract: str, token_contract: str, to_address: str):
        # Make sure that what is imported is actually a valid token
        tau, token = get_token_interface(tau_contract, token_contract)
        assert tau_contract != token_contract

        dex = get_dex_interface(dex_contract)
        assert not dex is None, 'Dex needs to be valid'

        tau_reserve, token_reserve = get_pair_reserves(tau_contract=tau_contract,token_contract=token_contract) # "gas savings"

        # 2 - Get Pair's balance
        last_total_tau_balance = pairs[tau_contract, 'balance']
        last_total_token_balance = pairs[token_contract, 'balance']

        # new total balances (new)
        current_total_tau_balance = tau.balance_of(ctx.this)
        current_total_token_balance = token.balance_of(ctx.this)

        pair_tau_balance = tau_reserve + (current_total_tau_balance - last_total_tau_balance)
        pair_token_balance = token_reserve + (current_total_token_balance - last_total_token_balance)

        lp_token_liquidity = balance_of(tau.token_name(), token.token_name(), ctx.this)

        # We update how to handle fees, before updating liquidity
        fee_on = mint_fee(dex, tau, token, tau_reserve, token_reserve)
        lp_token_supply = pairs[tau.token_name(), token.token_name(), 'lp_token_supply']

        tau_amount = (lp_token_liquidity * pair_tau_balance) / lp_token_supply # using balances ensures pro-rata distribution
        token_amount = (lp_token_liquidity * pair_token_balance) / lp_token_supply # using balances ensures pro-rata distribution
        assert tau_amount > 0 and token_amount > 0, 'Insufficient liquidity burned'

        # destroy lp tokens + return tokens
        burn_lp_tokens(tau, token, ctx.this, lp_token_liquidity)
        tau.transfer(tau_amount, to_address) # safe_transfer
        token.transfer(token_amount, to_address) # safe_transfer

        # Get new Dex balance
        current_total_tau_balance = tau.balance_of(ctx.this)
        current_total_token_balance = token.balance_of(ctx.this)

        pair_tau_balance = tau_reserve + (current_total_tau_balance - last_total_tau_balance)
        pair_token_balance = token_reserve + (current_total_token_balance - last_total_token_balance)

        # Update Pair internal state
        update(tau, token, pair_tau_balance, pair_token_balance)
        if(fee_on):
            # Update kLast to calculate fees
            pairs[tau.token_name(), token.token_name(), 'kLast'] = pair_tau_balance * pair_token_balance

        #emit Burn(ctx.signer, tau_amount, token_amount, to_address)
        return tau_amount, token_amount

    # TODO - B1/A5 - CallData / Emit Events
    # UniswapV2Pair.sol => swap()
    # This low-level function should be called from a contract which performs important safety checks
    @export
    def swap(tau_contract:str,  token_contract:str, tau_out:float, token_out:float, to_address:str):
        assert not (tau_out > 0 and token_out > 0), 'Only one Coin Out allowed'
        assert tau_out > 0 or token_out > 0, 'Insufficient Ouput Amount'

        # Make sure that what is imported is actually a valid token
        tau, token = get_token_interface(tau_contract, token_contract)
        assert tau_contract != token_contract

        tau_reserve, token_reserve = get_pair_reserves(
            tau_contract=tau_contract,
            token_contract=token_contract
        )
        assert tau_reserve > tau_out and token_reserve > token_out, 'UniswapV2: Insuficient Liquidity and Reserves'

        # optimistic transfer...
        if tau_out > 0 :
            tau.transfer(tau_out, to_address)
        if token_out > 0 :
            token.transfer(token_out, to_address)

        # Get new pair balances
        last_total_tau_balance = pairs[tau_contract, 'balance']
        last_total_token_balance = pairs[token_contract, 'balance']

        current_total_tau_balance = tau.balance_of(ctx.this)
        current_total_token_balance = token.balance_of(ctx.this)

        new_pair_tau_balance = tau_reserve + (current_total_tau_balance - last_total_tau_balance)
        new_pair_token_balance = token_reserve + (current_total_token_balance - last_total_token_balance)

        # TODO - B1 - Identify this call from UniV2
        # if (data.length > 0) IUniswapV2Callee(to).uniswapV2Call(msg.sender, amount0Out, amount1Out, data);

        # Calculate pair tau_in or token_in based on last/new balances
        tau_in = new_pair_tau_balance - (tau_reserve - tau_out) if new_pair_tau_balance > tau_reserve else 0
        token_in = new_pair_token_balance - (token_reserve - token_out) if new_pair_token_balance > token_reserve else 0
        assert tau_in > 0 or token_in > 0, 'UniswapV2: Insufficient Input Amount tau_in: {} token_in: {}'.format(tau_in, token_in)

        # # TODO - A1/A2 - Break down / understand Balance Adjusted K exception
        # tau_balance_adjusted = (tau_balance*1000)-(tau_in*3)
        # token_balance_adjusted = (token_balance*1000)-(token_in*3)
        # assert tau_balance_adjusted * token_balance_adjusted >= (tau_reserve * token_reserve) * (1000^2), 'UniswapV2: Exception: K'

        update(
            tau,
            token,
            new_pair_tau_balance,
            new_pair_token_balance
        )

        # TODO - B2 - Event Emitters?
        # emit Swap(msg.sender, amount0In, amount1In, amount0Out, amount1Out, to);

# TODO - A1 - Liquidity pools - mint / burn
# TODO - A1 - Reserves (gas savings) vs. Balance
# TODO - A1 - Minimum liquidity
# TODO - A2 - KLast
# TODO - A2 - Fees
# TODO - A2 - Fee To Functionality
# TODO - A3 - Migrator Functionality
# Public interface
def dex():
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

    dex_pairs_interface = [
        I.Func('get_length_pairs', args=())
    ]

    # Contract management variables
    fee_to = Variable()
    fee_to_setter = Variable()

    def zero_address():
        return '0'

    def get_dex_pairs_interface(dex_pairs_contract):
        dex_pairs = I.import_module(dex_pairs_contract)
        # assert I.enforce_interface(dex_pairs, dex_pairs_interface), 'Dex pairs contract does not meet the required interface'

        return dex_pairs

    # Get token modules, validate & return
    def get_token_interface(tau_contract, token_contract):
        # Make sure that what is imported is actually a valid token
        tau = I.import_module(tau_contract)
        assert I.enforce_interface(tau, token_interface), 'Tau contract does not meet the required interface'

        token = I.import_module(token_contract)
        assert I.enforce_interface(token, token_interface), 'Token contract does not meet the required interface'

        return tau, token

    # UniswapV2Library.sol => quote
    # given some amount of an asset and pair reserves, returns an equivalent amount of the other asset
    def quote(a_amount, a_reserve, b_reserve):
        assert a_amount > 0, 'Insufficient amount!'
        assert a_reserve > 0 and b_reserve > 0, 'Insufficient liquidity'
        b_amount = (a_amount * b_reserve) / a_reserve

        return b_amount

    @construct
    def seed(fee_to_setter_address:str):
        fee_to.set(zero_address())
        fee_to_setter.set(fee_to_setter_address)

    @export
    # Number of pairs created
    def length_pairs():
        return pairs['count']

    @export
    def fee_to():
        return fee_to.get()

    @export
    def set_fee_to(account:str):
        assert ctx.caller == fee_to_setter.get()
        fee_to.set(account)

    @export
    def fee_to_setter():
        return fee_to_setter.get()

    # Create pair before doing anything else
    @export
    def create_pair(dex_pairs: str, tau_contract: str, token_contract: str):
        # Make sure that what is imported is actually a valid token
        assert tau_contract != token_contract

        pairs = get_dex_pairs_interface(dex_pairs)
        assert pairs.pair(tau_contract, token_contract) is None, 'Market already exists!'

        # 1 - Create the pair
        # TODO - A4 - Make pair lookup, work vice/versa
        pairs.initialize(tau_contract, token_contract)

        # TODO - B1 - Support new functionality
        # 2 - Adds liquidity if provided
        # if (not tau_in is None and tau_in > 0) and (not token_in is None and token_in > 0) :
        #     add_liquidity(
        #         dex_pairs=dex_pairs,
        #         tau_contract=tau_contract,
        #         token_contract=token_contract,
        #         tau_in=tau_in,
        #         token_in=token_in)

    # # TODO - A1 - Add liquidity needs to implement add_liquidity + mint_liquidity
    # # TODO - A1 - Add liquidity needs to implement remove_liquidity + burn_liquidity
    # # Route01 Fn
    # # Pair must exist before liquidity can be added
    # @export
    # def add_liquidity(dex_pairs: str, tau_contract: str, token_contract: str, tau_in: int, token_in: int):
    #     assert token_in > 0
    #     assert tau_in > 0
    #
    #     # Make sure that what is imported is actually a valid token
    #     tau, token = get_token_interface(tau_contract, token_contract)
    #     assert tau_contract != token_contract
    #
    #     pairs = get_dex_pairs_interface(dex_pairs)
    #     assert not pairs.pair(tau_contract, token_contract) is None, 'Market does not exist!'
    #
    #     # 1 - This contract will own all amounts sent to it
    #     tau.transfer(tau_in, ctx.this)
    #     token.transfer(token_in, ctx.this)

        # # Track liquidity provided by signer
        # # TODO - If we care about "% pool" This needs to remain updated as market swings along X,Y
        # if pairs[tau_contract, token_contract, ctx.signer] is None :
        #     pairs[tau_contract, token_contract, 'tau_liquidity', ctx.signer] = tau_in
        #     pairs[tau_contract, token_contract, 'token_liquidity', ctx.signer] = token_in
        # else :
        #     pairs[tau_contract, token_contract, 'tau_liquidity', ctx.signer] += tau_in
        #     pairs[tau_contract, token_contract, 'token_liquidity', ctx.signer] += token_in
        #
        # # I'm assuming registry of [ctx.this,ctx.investor,amount] is done via LP
        # update(
        #     tau,
        #     token,
        #     tau.balance_of(ctx.this),
        #     token.balance_of(ctx.this),
        #     pairs[tau.token_name(), token.token_name(), 'tau_reserve'],
        #     pairs[tau.token_name(), token.token_name(), 'token_reserve']
        # )

MINIMUM_LIQUIDITY = pow(10,3)
TOKEN_DECIMALS = 18
STARTING_BALANCE = 10000

# All test values for tests, taken from UniswapV2Pair.specs.ts
# Tests do not validate against functionality that was never tested, such as:
# TODO - A2 - Complete UniswapV2: K exceptions
# TODO - A4 - Token Supply Validations.
class PairSpecs(TestCase):

    # returns ContractingDecimal
    def expand_to_token_decimals(self, amount):
        return ContractingDecimal(amount / pow(10,TOKEN_DECIMALS))

    # before each test, setup the conditions
    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        self.fee_to_address = 'fee_to_address'
        self.fee_to_setter_address = 'fee_to_setter_address'
        self.wallet_address = 'wallet_address'

        # TODO - A2 - Complete UniswapV2: K exceptions.
        # token0
        self.client.submit(tau, 'tau', constructor_args={
            's_name': 'tau',
            's_symbol': 'TAU',
            'vk': self.wallet_address,
            'vk_amount': 10000
        })

        # token1
        self.client.submit(eth, 'eth', constructor_args={
            's_name': 'eth',
            's_symbol': 'ETH',
            'vk': self.wallet_address,
            'vk_amount': 10000
        })

        # Dex
        self.client.submit(dex, 'dex', constructor_args={
            'fee_to_setter_address': self.fee_to_setter_address
        })

        # Dex Pairs
        # Initialize ownership to dex
        self.client.submit(dex_pairs, 'dex_pairs', constructor_args={
            'owner_address': 'dex'
        })

        # Change tx signer to actor1
        self.change_signer(self.wallet_address)

        # Create pair on Dex
        self.dex.create_pair(
            dex_pairs='dex_pairs',
            tau_contract='tau',
            token_contract='eth'
        )

    def change_signer(self, name):
        self.client.signer = name

        self.tau = self.client.get_contract('tau')
        self.eth = self.client.get_contract('eth')
        self.dex = self.client.get_contract('dex')
        self.dex_pairs = self.client.get_contract('dex_pairs')

    def zero_address(self):
        return '0'

    def test_1_mint(self):
        self.change_signer(self.wallet_address)

        tau_amount = 1.0
        eth_amount = 4.0

        self.tau.transfer(amount=tau_amount, to=self.dex_pairs.name)
        self.eth.transfer(amount=eth_amount, to=self.dex_pairs.name)

        expected_liquidity = 2.0
        token_mint_address, tau_amount, token_amount = self.dex_pairs.mint_liquidity(
            dex_contract=self.dex.name,
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            to_address=self.wallet_address
        )

        # TODO - A4 - Asserts on Emit()
        total_supply = self.dex_pairs.total_supply(tau_contract=self.tau.name, token_contract=self.eth.name)
        assert total_supply == expected_liquidity, 'Invalid Total supply'

        zero_address_balance = self.dex_pairs.balance_of(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            account=self.zero_address()
        )
        assert zero_address_balance == self.expand_to_token_decimals(MINIMUM_LIQUIDITY), 'Invalid minimum liquidity initialized'

        wallet_address_balance = self.dex_pairs.balance_of(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            account=self.wallet_address
        )
        assert wallet_address_balance == expected_liquidity - self.expand_to_token_decimals(MINIMUM_LIQUIDITY), 'Invalid balance initialized'

        assert self.tau.balance_of(account=self.dex_pairs.name) == tau_amount, 'Invalid tau balance'
        assert self.eth.balance_of(account=self.dex_pairs.name) == eth_amount, 'Invalid ethereum balance'

        tau_reserves, token_reserves = self.dex_pairs.get_pair_reserves(
            tau_contract=self.tau.name,
            token_contract=self.eth.name
        )

        assert tau_reserves == tau_amount, 'Invalid tau reserves'
        assert token_reserves == eth_amount, 'Invalid eth reserves'

    def add_liquidity(self, tau_amount, token_amount):
        self.tau.transfer(amount=tau_amount, to=self.dex_pairs.name)
        self.eth.transfer(amount=token_amount, to=self.dex_pairs.name)

        self.dex_pairs.mint_liquidity(
            dex_contract=self.dex.name,
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            to_address=self.wallet_address
        )

    def test_2_0_swap_tests(self):
        swap_test_cases = [
            [1, 5, 10, '1662497915624478906'],
            [1, 10, 5, '453305446940074565'],

            [2, 5, 10, '2851015155847869602'],
            [2, 10, 5, '831248957812239453'],

            [1, 10, 10, '906610893880149131'],
            [1, 100, 100, '987158034397061298'],
            [1, 1000, 1000, '996006981039903216']
        ]

        swap_test_cases = map(
            lambda case:
            map(
                lambda x:
                self.expand_to_token_decimals(int(x)) if isinstance(x, str) else ContractingDecimal(int(x)),
                case
            ),
            swap_test_cases
        )

        index = 0
        for test_case in swap_test_cases :
            self.setUp()

            swap_amount, tau_amount, token_amount, expected_output_amount = test_case

            index += 1
            print("Test Case [#{}] with params: [{},{},{},{}]".format(index, swap_amount, tau_amount, token_amount, expected_output_amount))

            self.add_liquidity(tau_amount, token_amount)
            self.tau.transfer(amount=swap_amount, to=self.dex_pairs.name)

            # TODO - A2 - Complete UniswapV2: K exceptions
            # with self.assertRaises(Exception) as context:
            # self.dex_pairs.swap(
            #     tau_contract=self.tau.name,
            #     token_contract=self.eth.name,
            #     tau_out=0,
            #     token_out=expected_output_amount + 1.0, # swap more
            #     to_address=self.wallet_address
            # )
            # self.assertTrue('UniswapV2: K' in context.exception, 'UniswapV2 ')

            self.dex_pairs.swap(
                tau_contract=self.tau.name,
                token_contract=self.eth.name,
                tau_out=0,
                token_out=expected_output_amount,
                to_address='test_results_wallet'
            )

            # Validate Reserves
            tau_reserve, token_reserve = self.dex_pairs.get_pair_reserves(
                tau_contract=self.tau.name,
                token_contract=self.eth.name
            )

            self.assertEqual(tau_reserve, tau_amount + swap_amount)
            self.assertEqual(token_reserve, token_amount - expected_output_amount)

            wallet_balance_tau = self.tau.balance_of(account='test_results_wallet')
            wallet_balance_token = self.eth.balance_of(account='test_results_wallet')
            self.assertEqual(wallet_balance_tau, 0)
            self.assertEqual(wallet_balance_token, expected_output_amount)

    def test_3_token0_swap(self):
        self.change_signer(self.wallet_address)

        tau_amount = 5
        token_amount = 10

        self.add_liquidity(tau_amount, token_amount)

        swap_amount = 1
        expected_output_amount = self.expand_to_token_decimals(1662497915624478906)

        self.tau.transfer(amount=swap_amount, to=self.dex_pairs.name)

        # TODO - A4 - Asserts on Emit()
        self.dex_pairs.swap(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            tau_out=0,
            token_out=expected_output_amount,
            to_address='test_results_wallet'
        )
        # Validate Wallet Balances Post Swap
        wallet_balance_tau = self.tau.balance_of(account='test_results_wallet')
        self.assertEqual(wallet_balance_tau, 0.0)
        wallet_balance_token = self.eth.balance_of(account='test_results_wallet')
        self.assertEqual(wallet_balance_token, expected_output_amount)

        # Validate Reserves
        tau_reserve, token_reserve = self.dex_pairs.get_pair_reserves(
            tau_contract=self.tau.name,
            token_contract=self.eth.name
        )

        self.assertEqual(tau_reserve, tau_amount + swap_amount)
        self.assertEqual(token_reserve, token_amount - expected_output_amount)

        # Validate Balances + AMM Reserves Post-Swap
        pair_balance_tau = self.tau.balance_of(account=self.dex_pairs.name)
        self.assertEqual(pair_balance_tau, tau_amount + swap_amount)
        pair_balance_token = self.eth.balance_of(account=self.dex_pairs.name)
        self.assertEqual(pair_balance_token, token_amount - expected_output_amount)

        # TODO - A4 - Token Supply Validations.
        # Validate Supply @ UniswapV2Pair.specs.ts
        total_supply = self.dex_pairs.total_supply(
            tau_contract=self.tau.name,
            token_contract=self.eth.name
        )

    def test_3_token1_swap(self):
        self.change_signer(self.wallet_address)

        tau_amount = 5
        token_amount = 10

        self.add_liquidity(tau_amount, token_amount)

        swap_amount = 1
        expected_output_amount = self.expand_to_token_decimals(453305446940074565)

        self.eth.transfer(amount=swap_amount, to=self.dex_pairs.name)

        # TODO - A4 - Asserts on Emit()
        self.dex_pairs.swap(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            tau_out=expected_output_amount,
            token_out=0,
            to_address='test_results_wallet'
        )

        # Validate Wallet Balances Post Swap
        wallet_balance_tau = self.tau.balance_of(account='test_results_wallet')
        self.assertEqual(wallet_balance_tau, expected_output_amount)
        wallet_balance_token = self.eth.balance_of(account='test_results_wallet')
        self.assertEqual(wallet_balance_token, 0.0)

        # Validate Reserves
        tau_reserve, token_reserve = self.dex_pairs.get_pair_reserves(
            tau_contract=self.tau.name,
            token_contract=self.eth.name
        )

        self.assertEqual(tau_reserve, tau_amount - expected_output_amount)
        self.assertEqual(token_reserve, token_amount + swap_amount)

        # Validate Balances + AMM Reserves Post-Swap
        pair_balance_tau = self.tau.balance_of(account=self.dex_pairs.name)
        self.assertEqual(pair_balance_tau, tau_amount - expected_output_amount)
        pair_balance_token = self.eth.balance_of(account=self.dex_pairs.name)
        self.assertEqual(pair_balance_token, token_amount + swap_amount)

        # TODO - A4 - Token Supply Validations.
        # Validate Supply @ UniswapV2Pair.specs.ts
        total_supply = self.dex_pairs.total_supply(
            tau_contract=self.tau.name,
            token_contract=self.eth.name
        )

    def test_4_burn(self):
        self.change_signer(self.wallet_address)

        tau_amount = 3
        token_amount = 3

        # Add liquidity
        self.add_liquidity(tau_amount, token_amount)

        expected_liquidity = 3

        self.dex_pairs.transfer(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            amount=expected_liquidity-self.expand_to_token_decimals(MINIMUM_LIQUIDITY),
            to=self.dex_pairs.name
        )

        dex_pair_lp_balance = self.dex_pairs.balance_of(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            account=self.dex_pairs.name
        )
        assert dex_pair_lp_balance == expected_liquidity-self.expand_to_token_decimals(MINIMUM_LIQUIDITY)

        # transfer, transfer, transfer, sync, burn
        tau_amount, token_amount = self.dex_pairs.burn_liquidity(
            dex_contract=self.dex.name,
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            to_address=self.wallet_address
        )

        # Assert we got back everything - MINIMUM LIQUIDITY
        assert tau_amount == token_amount
        assert tau_amount == expected_liquidity-self.expand_to_token_decimals(MINIMUM_LIQUIDITY)
        assert token_amount == expected_liquidity-self.expand_to_token_decimals(MINIMUM_LIQUIDITY)

        tau_wallet_balance = self.tau.balance_of(account=self.wallet_address)
        assert tau_wallet_balance == STARTING_BALANCE - self.expand_to_token_decimals(MINIMUM_LIQUIDITY)
        token_wallet_balance = self.eth.balance_of(account=self.wallet_address)
        assert token_wallet_balance == STARTING_BALANCE - self.expand_to_token_decimals(MINIMUM_LIQUIDITY)

        # Assert that remaining balance of liquidity for wallet is 0
        assert self.dex_pairs.balance_of(tau_contract=self.tau.name, token_contract=self.eth.name, account=self.wallet_address) == 0
        # assert total supply left for token pair is the MINIMUM_LIQUIDITY
        assert self.dex_pairs.total_supply(tau_contract=self.tau.name, token_contract=self.eth.name) == self.expand_to_token_decimals(MINIMUM_LIQUIDITY)

        # assert total currency left on currencies is only the minimum liquidity
        assert self.tau.balance_of(account=self.dex_pairs.name) == self.expand_to_token_decimals(MINIMUM_LIQUIDITY)
        assert self.eth.balance_of(account=self.dex_pairs.name) == self.expand_to_token_decimals(MINIMUM_LIQUIDITY)

    # Test = Dex.fee_to is not initialized (feeTo is Off)
    def test_5_feeTo_off(self):
        tau_amount = 1000
        eth_amount = 1000
        self.add_liquidity(tau_amount, eth_amount)

        swap_amount = 1
        expected_output_amount = self.expand_to_token_decimals(996006981039903216)
        self.eth.transfer(amount=swap_amount, to=self.dex_pairs.name)
        self.dex_pairs.swap(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            tau_out=expected_output_amount,
            token_out=0,
            to_address='test_results_wallet'
        )

        # Validate Reserves
        tau_reserve, token_reserve = self.dex_pairs.get_pair_reserves(
            tau_contract=self.tau.name,
            token_contract=self.eth.name
        )
        self.assertEqual(tau_reserve, tau_amount - expected_output_amount)
        self.assertEqual(token_reserve, eth_amount + swap_amount)

        wallet_balance_tau = self.tau.balance_of(account='test_results_wallet')
        wallet_balance_token = self.eth.balance_of(account='test_results_wallet')
        self.assertEqual(wallet_balance_tau, expected_output_amount)
        self.assertEqual(wallet_balance_token, 0)

        expected_liquidity = 1000

        self.dex_pairs.transfer(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            amount=expected_liquidity-self.expand_to_token_decimals(MINIMUM_LIQUIDITY),
            to=self.dex_pairs.name
        )

        dex_pair_lp_balance = self.dex_pairs.balance_of(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            account=self.dex_pairs.name
        )
        assert dex_pair_lp_balance == expected_liquidity-self.expand_to_token_decimals(MINIMUM_LIQUIDITY)

        self.dex_pairs.burn_liquidity(
            dex_contract=self.dex.name,
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            to_address=self.wallet_address
        )

        # Total supply remains as MINIMUM LIQUIDITY
        pair_total_supply = self.dex_pairs.total_supply(tau_contract=self.tau.name, token_contract=self.eth.name)
        assert pair_total_supply == self.expand_to_token_decimals(MINIMUM_LIQUIDITY)

    # Test = Dex.fee_to gets initialized (feeTo is On)
    def test_5_feeTo_on(self):
        # Initialize dex.fee_to
        self.change_signer(self.fee_to_setter_address)
        self.dex.set_fee_to(account=self.fee_to_address)

        self.change_signer(self.wallet_address)

        tau_amount = 1000
        eth_amount = 1000
        self.add_liquidity(tau_amount, eth_amount)

        swap_amount = 1
        expected_output_amount = self.expand_to_token_decimals(996006981039903216)
        self.eth.transfer(amount=swap_amount, to=self.dex_pairs.name)
        self.dex_pairs.swap(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            tau_out=expected_output_amount,
            token_out=0,
            to_address='test_results_wallet'
        )

        # Validate Reserves
        tau_reserve, token_reserve = self.dex_pairs.get_pair_reserves(
            tau_contract=self.tau.name,
            token_contract=self.eth.name
        )
        self.assertEqual(tau_reserve, tau_amount - expected_output_amount)
        self.assertEqual(token_reserve, eth_amount + swap_amount)

        wallet_balance_tau = self.tau.balance_of(account='test_results_wallet')
        wallet_balance_token = self.eth.balance_of(account='test_results_wallet')
        self.assertEqual(wallet_balance_tau, expected_output_amount)
        self.assertEqual(wallet_balance_token, 0)

        expected_liquidity = 1000

        self.dex_pairs.transfer(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            amount=expected_liquidity-self.expand_to_token_decimals(MINIMUM_LIQUIDITY),
            to=self.dex_pairs.name
        )

        dex_pair_lp_balance = self.dex_pairs.balance_of(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            account=self.dex_pairs.name
        )
        assert dex_pair_lp_balance == expected_liquidity-self.expand_to_token_decimals(MINIMUM_LIQUIDITY)

        self.dex_pairs.burn_liquidity(
            dex_contract=self.dex.name,
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            to_address=self.wallet_address
        )

        # Total supply remains as MINIMUM LIQUIDITY
        # ContractingDecimal carries more precision than Ethereum bigNumber
        # assert to 17 places
        expected_supply = self.expand_to_token_decimals(249750499251388 + MINIMUM_LIQUIDITY)
        pair_total_supply = self.dex_pairs.total_supply(tau_contract=self.tau.name, token_contract=self.eth.name)
        self.assertAlmostEqual(pair_total_supply, expected_supply, places=17)

        fee_to_balance = self.dex_pairs.balance_of(
            tau_contract=self.tau.name,
            token_contract=self.eth.name,
            account=self.fee_to_address
        )
        expected_fee_to_balance = self.expand_to_token_decimals(249750499251388)
        self.assertAlmostEqual(fee_to_balance, expected_fee_to_balance, places=17)

        tau_balance = self.tau.balance_of(account=self.dex_pairs.name)
        expected_tau_balance = self.expand_to_token_decimals(249501683697445 + MINIMUM_LIQUIDITY)
        self.assertAlmostEqual(tau_balance, expected_tau_balance, places=17)

        token_balance = self.eth.balance_of(account=self.dex_pairs.name)
        expected_token_balance = self.expand_to_token_decimals(250000187312969 + MINIMUM_LIQUIDITY)
        self.assertAlmostEqual(token_balance, expected_token_balance, places=17)
