import math
from unittest import TestCase
from contracting.client import ContractingClient

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

def dex_pairs():
    # BASE PAIR STATE
    # Token
    # token = import_module(token_contract: str)
    # Token Balance
    # balance = _token.balance(address: str)
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

    # # TODO - Verifiy minimum liquidity
    # MINIMUM_LIQUIDITY = 1
    # TOKEN_DECIMALS = 18
    #
    # # TODO - A2 - Validate safe_transfer works for TAU + Other tokens
    # # Pair Fn
    # def safe_transfer(token, to, amount) :
    #     results = token.transfer(to, amount)
    #     assert results and isinstance(results, bool) and results == True, 'Transfer Failed'
    #
    # # TODO - A2 - Implement Jeff's "Valid Hex Address"
    # # Get zero address
    # def zero_address():
    #     return '0'
    #
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
    #
    # # From UniV2Pair.sol
    # def update(tau, token, tau_balance, token_balance, tau_reserve_last, token_reserve_last):
    #     pairs[tau.token_name(), token.token_name(), 'tau_reserve'] = tau_balance
    #     pairs[tau.token_name(), token.token_name(), 'token_reserve'] = token_balance
    #
    # # TODO - A1 - VALIDATE IMPLEMENTATION/SECURITY
    # # Currency/Pair Fn - Internal Interface
    # def mint_lp_tokens(tau, token, to_address:str, value: int) :
    #     # Increase LP Token supply
    #     lp_token_supply = pairs[tau.token_name(), token.token_name(), 'lp_token_supply']
    #     lp_token_supply += value
    #
    #     # Increase Acct LP Token balance
    #     lp_token_balance = pairs[tau.token_name(), token.token_name(), 'lp_token_balance', to_address]
    #     lp_token_balance = lp_token_balance + value
    #
    #     # return new supply, and balance
    #     #emit Transfer(address_zero(), to, value)
    #     return pairs[tau.token_name(), token.token_name(), 'lp_token_supply'], pairs[tau.token_name(), token.token_name(), 'lp_token_balance', to_address]
    #
    # # TODO - A1 - VALIDATE IMPLEMENTATION/SECURITY
    # # Currency/Pair Fn - Internal Interface
    # def burn_lp_tokens(tau, token, from_address: str, value: int) :
    #     # Decrease LP Token supply
    #     lp_token_supply = pairs[tau.token_name(), token.token_name(), 'lp_token_supply']
    #     lp_token_supply = lp_token_supply - value
    #
    #     # Decrease Acct LP Token balance
    #     lp_token_balance = pairs[tau.token_name(), token.token_name(), 'lp_token_balance', from_address]
    #     lp_token_balance = lp_token_balance - value
    #
    #     # return new supply, and balance
    #     # emit Transfer(address_zero(), to, value)
    #     return pairs[tau.token_name(), token.token_name(), 'lp_token_supply'], pairs[tau.token_name(), token.token_name(), 'lp_token_balance', from_address]
    #
    # # TODO - A1 - VALIDATE IMPLEMENTATION/SECURITY
    # # DONE - PORTED + REVIEWED
    # # UniswapV2Pai.sol => _mintFee()
    # def mint_fee(dex, tau, token, tau_reserve, token_reserve):
    #     lp_token_supply = pairs[tau.token_name(), token.token_name(), 'lp_token_supply']
    #
    #     fee_to = dex.fee_to()
    #     fee_on = fee_to != zero_address() # make sure we're not burning the fee?
    #     kLast = pairs[tau.token_name(), token.token_name(), 'kLast'] # "gas savings"
    #     if(fee_on) :
    #         if(kLast != 0) :
    #             rootK = math.sqrt(tau_reserve * token_reserve)
    #             rootKLast = math.sqrt(kLast)
    #             if(rootK > rootKLast) :
    #                 numerator = lp_token_supply * (rootK - rootKLast)
    #                 denominator = (rootK * 5) + rootKLast
    #                 liquidity = numerator / denominator
    #                 if(liquidity > 0):
    #                     mint_lp_tokens(tau, token, fee_to, liquidity)
    #     elif(kLast != 0) :
    #         pairs[tau.token_name(), token.token_name(), 'kLast'] = 0
    #
    #     return fee_on

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
    def initialize(tau_contract:str, token_contract:str):
        assert ctx.caller == owner.get(), 'TauSwa-DexPairs: FORBIDDEN'
        
        pairs[tau_contract, token_contract] = token_contract
        pairs[tau_contract, token_contract, 'tau_reserve'] = 0
        pairs[tau_contract, token_contract, 'token_reserve'] = 0
        pairs[tau_contract, token_contract, 'lp_token_supply'] = 0
        pairs[tau_contract, token_contract, 'kLast'] = 0
        pairs['count'] += 1

    # @export
    # # Returns the total reserves from each tau/token
    # def get_reserves(tau_contract:str, token_contract:str):
    #     return pairs[tau_contract, token_contract, 'tau_reserve'], \
    #             pairs[tau_contract, token_contract, 'token_reserve']
    #
    # @export
    # # Pass contracts + tokens_in, get: tokens_out, slippage
    # def get_trade_details(tau_contract: str, token_contract: str, tau_in: int, token_in: int):
    #     return calculate_trade_details(tau_contract, token_contract, tau_in, token_in)
    #
    # # TODO - A1 - VALIDATE IMPLEMENTATION
    # # UniswapV2Pair.sol => mint()
    # # This low-level function should be called from a contract which performs important safety checks
    # @export
    # def mint_liquidity(dex, tau, token, to):
    #     # 1 - State reserves (current state)
    #     tau_reserve, token_reserve = get_reserves(tau.token_name, token.token_name) # "gas savings"
    #     # 2 - Token reserves (new state)
    #     tau_balance = tau.balance_of(ctx.this)
    #     token_balance = token.balance_of(ctx.this)
    #     # 3 - How many tokens were added
    #     tau_amount = tau_balance - tau_reserve
    #     token_amount = token_balance - token_reserve
    #
    #     # We update how to handle fees, before updating liquidity
    #     fee_on = mint_fee(dex, tau, token, tau_reserve, token_reserve)
    #     lp_token_supply = pairs[tau.token_name(), token.token_name(), 'lp_token_supply'] # "gas savings"
    #     if(lp_token_supply == 0 ) :
    #         # TODO - Migrator logic
    #         # Initial liquidity = SeedLiquidity - MinimumLiquidity-
    #         liquidity = math.sqrt(tau_amount * token_amount) - MINIMUM_LIQUIDITY
    #         mint_lp_tokens(tau, token, zero_address(), MINIMUM_LIQUIDITY) # permanently lock the first MINIMUM_LIQUIDITY tokens
    #     else :
    #         # Get new liquidity
    #         liquidity = min(
    #             ( tau_amount * lp_token_supply ) / tau_reserve,
    #             ( token_amount * lp_token_supply ) / token_reserve
    #         )
    #
    #     # Assign LP Tokens to provider
    #     assert liquidity > 0, 'Insufficient liquidity minted'
    #     mint_lp_tokens(tau, token, to, liquidity)
    #
    #     # Update Pair internal state
    #     update(tau, token, tau_balance, token_balance, tau_reserve, token_reserve)
    #     if(fee_on) :
    #         # tau_reserve & token_reserve are up-to-date
    #         # Update kLast to calculate fees
    #         pairs[tau.tau.token_name(), token.token_name(), 'kLast'] = tau_reserve * token_reserve
    #
    #     #emit Mint(ctx.signer, tau_amount, token_amount)
    #     return liquidity
    #
    # # TODO - A1 - Finish Implementation + Validate
    # # UniswapV2Pai.sol => burn()
    # # This low-level function should be called from a contract which performs important safety checks
    # @export
    # def burn_liquidity(dex, tau, token, to_address):
    #     tau_reserve, token_reserve = get_reserves(tau.token_name, token.token_name) # gas savings
    #     tau_balance = tau.balance_of(ctx.this)
    #     token_balance = token.balance_of(ctx.this)
    #     lp_token_liquidity = pairs[tau.tau.token_name(), token.token_name(), 'lp_token_balance', ctx.this]
    #
    #     # We update how to handle fees, before updating liquidity
    #     fee_on = mint_fee(dex, tau, token, tau_reserve, token_reserve)
    #     lp_token_supply = pairs[tau.token_name(), token.token_name(), 'lp_token_supply']
    #     tau_amount = (lp_token_liquidity * tau_balance) / lp_token_supply # using balances ensures pro-rata distribution
    #     token_amount = (lp_token_liquidity * token_balance) / lp_token_supply # using balances ensures pro-rata distribution
    #     assert tau_amount > 0 and token_amount > 0, 'Insufficient liquidity burned'
    #
    #     # destroy lp tokens + return tokens
    #     burn_lp_tokens(tau, token, ctx.this, lp_token_liquidity)
    #     safe_transfer(tau, to_address, tau_amount)
    #     safe_transfer(token, to_address, token_amount)
    #
    #     # Get new Dex balance
    #     tau_balance = tau.balance_of(ctx.this)
    #     token_balance = token.balance_of(ctx.this)
    #
    #     # Update Pair internal state
    #     update(tau, token, tau_balance, token_balance, tau_reserve, token_reserve)
    #     if(fee_on):
    #         # Update kLast to calculate fees
    #         pairs[tau.tau.token_name(), token.token_name(), 'kLast'] = tau_reserve * token_reserve
    #
    #     #emit Burn(ctx.signer, tau_amount, token_amount, to_address)
    #     return tau_amount, token_amount
    #
    # # TODO - A1 - Swap needs to be implement liquidity/fees
    # # UniswapV2Pair.sol => swap()
    # # This low-level function should be called from a contract which performs important safety checks
    # # function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external lock {
    # @export
    # def swap(tau, token, tau_out, token_out, to):
    #     assert not (tau_out > 0 and token_out > 0), 'Only one Coin Out allowed'
    #     assert tau_out > 0 or token_out > 0, 'Insufficient Ouput Amount'
    #
    #     tau_reserve, token_reserve = get_reserves(tau.token_name(), token.token_name())
    #     assert tau_reserve > tau_out and token_reserve > token_out, 'UniswapV2: Inssuficient Liquidity'
    #
    #     # TODO - WARN - Optimistic send...
    #     # TODO - A2 - Why is this called BEFORE downstream asserts?
    #     # TODO - A2 - How is SOL.safe_transfer() != TAU.transfer_from()
    #     if tau_out > 0 : safe_transfer(tau, to, tau_out)
    #     if token_out > 0 : safe_transfer(token, to, token_out)
    #
    #     # TODO - B1 - Identify this call from UniV2
    #     # if (data.length > 0) IUniswapV2Callee(to).uniswapV2Call(msg.sender, amount0Out, amount1Out, data);
    #
    #     tau_balance = tau.balance_of(ctx.this)
    #     token_balance = token.balance_of(ctx.this)
    #
    #     # Assert amounts being passed in will work for existing reserves/balances
    #     tau_in = tau_balance - ( tau_reserve - tau_out) if tau_balance > tau_reserve - tau_out else 0
    #     token_in = token_balance - ( token_reserve - token_out) if token_balance > token_reserve - tau_out else 0
    #     assert tau_in > 0 or token_in > 0, 'UniswapV2: Insufficient Input Amount'
    #
    #     # TODO - A1/A2 - Deconstruct Curve Adjustment Calculation
    #     # tau_balance_adjusted = (tau_balance*1000)-(tau_in*3)
    #     # token_balance_adjusted = (token_balance*1000)-(token_in*3)
    #     # assert tau_balance_adjusted * token_balance_adjusted >= (tau_reserve * token_reserve) * (1000^2), 'UniswapV2: Exception: K'
    #
    #     # TODO - A1/A2 - Implement update function
    #     update(tau, token, tau_balance, token_balance, tau_reserve, token_reserve)
    #
    #     # TODO - B2 - Event Emitters?
    #     # emit Swap(msg.sender, amount0In, amount1In, amount0Out, amount1Out, to);

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

    # TODO - Verifiy minimum liquidity
    MINIMUM_LIQUIDITY = 1
    TOKEN_DECIMALS = 18

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
        fee_to_setter = fee_to_setter_address

    @export
    # Number of pairs created
    def length_pairs():
        return pairs['count']

    # Create pair before doing anything else
    @export
    def create_pair(dex_pairs: str, tau_contract: str, token_contract: str, tau_in: int, token_in: int):
        # Make sure that what is imported is actually a valid token
        pairs = get_dex_pairs_interface(dex_pairs)
        # tau, token = get_token_interface(tau_contract, token_contract)

        assert tau_contract != token_contract
        assert pairs.pair(tau_contract, token_contract) is None, 'Market already exists!'

        # 1 - Create the pair
        pairs.initialize(tau_contract, token_contract)

        # 2 - Adds liquidity if provided
        # if (not tau_in is None and tau_in > 0) and (not token_in is None and token_in > 0) :
        #     add_liquidity(tau_contract, token_contract, tau_in, token_in)

    # # TODO - A1 - Add liquidity needs to implement add_liquidity + mint_liquidity
    # # TODO - A1 - Add liquidity needs to implement remove_liquidity + burn_liquidity
    # # Route01 Fn
    # # Pair must exist before liquidity can be added
    # @export
    # def add_liquidity(tau_contract: str, token_contract: str, tau_in: int, token_in: int):
    #     assert token_in > 0
    #     assert tau_in > 0
    #
    #     # Make sure that what is imported is actually a valid token
    #     tau, token = get_token_interface(tau_contract, token_contract)
    #
    #     assert tau_contract != token_contract
    #     assert not pairs[tau_contract, token_contract] is None, 'Market does not exist!'
    #
    #     # 1 - This contract will own all amounts sent to it
    #     tau.transfer(tau_in, ctx.this)
    #     token.transfer(token_in, ctx.this)
    #
    #     # Track liquidity provided by signer
    #     # TODO - If we care about "% pool" This needs to remain updated as market swings along X,Y
    #     if pairs[tau_contract, token_contract, ctx.signer] is None :
    #         pairs[tau_contract, token_contract, 'tau_liquidity', ctx.signer] = tau_in
    #         pairs[tau_contract, token_contract, 'token_liquidity', ctx.signer] = token_in
    #     else :
    #         pairs[tau_contract, token_contract, 'tau_liquidity', ctx.signer] += tau_in
    #         pairs[tau_contract, token_contract, 'token_liquidity', ctx.signer] += token_in
    #
    #     # I'm assuming registry of [ctx.this,ctx.investor,amount] is done via LP
    #     update(
    #         tau,
    #         token,
    #         tau.balance_of(ctx.this),
    #         token.balance_of(ctx.this),
    #         pairs[tau.token_name(), token.token_name(), 'tau_reserve'],
    #         pairs[tau.token_name(), token.token_name(), 'token_reserve']
    #     )

MINIMUM_LIQUIDITY = 1
class PairSpecs(TestCase):

    # before each test, setup the conditions
    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        self.fee_to_setter_address = 'fee_to_setter_address'
        self.pair_address = 'pair_address'
        self.wallet_address = 'wallet_address'

        # token0
        self.client.submit(tau, 'tau', constructor_args={
            's_name': 'tau',
            's_symbol': 'TAU',
            'vk': 'actor1',
            'vk_amount': 15
        })

        # token1
        self.client.submit(eth, 'eth', constructor_args={
            's_name': 'eth',
            's_symbol': 'ETH',
            'vk': 'actor1',
            'vk_amount': 15
        })

        # Testing - Contract Objects
        self.tau = self.client.get_contract('tau')
        self.eth = self.client.get_contract('eth')

        # Dex
        self.client.submit(dex, 'dex', constructor_args={
            'fee_to_setter_address': self.fee_to_setter_address
        })
        self.dex = self.client.get_contract('dex')

        # Pair
        self.client.submit(dex_pairs, 'dex_pairs', constructor_args={
            'owner_address': 'dex'
        })
        self.dex_pairs = self.client.get_contract('dex_pairs')

        # Initialize pair
        self.dex.create_pair(
            dex_pairs='dex_pairs',
            tau_contract='tau',
            token_contract='eth',
            tau_in=10,
            token_in=10
        )

    def change_signer(self, name):
        self.client.signer = name

        self.tau = self.client.get_contract('tau')
        self.eth = self.client.get_contract('eth')
        self.dex = self.client.get_contract('dex')

    def zero_address(self):
        return '0'

    def test_mint(self):
        self.change_signer('actor1')
        #
        # tau_amount = 1.0
        # eth_amount = 4.0
        #
        # self.tau.transfer(self.dex, tau_amount)
        # self.eth.transfer(self.dex, eth_amount)
        #
        # expected_liquidity = 2.0
        # mint_address, tau_minted, token_minted = self.dex_pairs.mint_liquidity(
        #     self.dex,
        #     self.tau,
        #     self.eth,
        #     self.wallet_address
        # )
        #
        # # TODO - Asserts on Emit()
        # assert self.dex_pairs.balance(self.zero_address()) == MINIMUM_LIQUIDITY, 'Minimum liquidity initialized'
        # assert self.dex_pairs.balance(self.wallet_address) == expected_liquidity - MINIMUM_LIQUIDITY, 'Expected liquidity initialized'
        # assert not mint_address is None and not tau_minted is None and not token_minted is None, 'Pair minted'
        #
        # assert self.dex_pairs.total_supply == expected_liquidity, 'Invalid Total supply'
        # assert self.dex_pairs.balance_of(self.wallet_address) == expected_liquidity - MINIMUM_LIQUIDITY, 'Invalid balance initialized'
        # assert self.tau.balance_of(self.pair_address) == tau_amount, 'Invalid tau balance'
        # assert self.eth.balance_of(self.pair_address) == eth_amount, 'Invalid ethereum balance'
        #
        # reserves = self.dex_pairs.get_reserves()
        # assert reserves[0] == tau_amount, 'Invalid tau reserves'
        # assert reserves[1] == eth_amount, 'Invalid eth reserves'
