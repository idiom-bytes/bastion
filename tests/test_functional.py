from unittest import TestCase
from contracting.client import ContractingClient

def tau() :
    balances = Hash(default_value=0)
    token_name = Variable()
    token_symbol = Variable()

    # Cannot set breakpoint in @construct
    @construct
    def seed(s_name:str, s_symbol: str, vk: str):
        # Overloading this to mint tokens
        token_name.set(s_name)
        token_symbol.set(s_symbol)
        balances[vk] = 100

    @export
    def token_name():
        return token_name.get()

    @export
    def token_symbol():
        return token_symbol.get()

    @export
    def transfer(amount: float, to: str):
        assert amount > 0, 'Cannot send negative balances!'

        # why is this caller, and not signer?
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
    def transfer_from(amount: float, to: str, main_account: str):
        assert amount > 0, 'Cannot send negative balances!'

        # why is this caller, and not signer?
        # if we have a contract calling this, although signed by someone else, this will not work
        sender = ctx.caller

        # Why [main_acount,sender] & [sender] -= amount... shouldn't it be?
        # assert main_account == ctx.signer
        # balances[main_account] -= amount
        # balances[to] += amount
        assert balances[main_account, sender] >= amount, 'Not enough Tau approved to send! You have {} and are trying to spend {}'.format(balances[main_account, sender], amount)
        assert balances[main_account] >= amount, 'Not enough coins to send!'

        balances[main_account, sender] -= amount
        balances[main_account] -= amount

        balances[to] += amount

def eth() :
    balances = Hash(default_value=0)
    token_name = Variable()
    token_symbol = Variable()

    # Cannot set breakpoint in @construct
    @construct
    def seed(s_name:str, s_symbol: str, vk: str):
        # Overloading this to mint tokens
        token_name.set(s_name)
        token_symbol.set(s_symbol)
        balances[vk] = 100

    @export
    def token_name():
        return token_name.get()

    @export
    def token_symbol():
        return token_symbol.get()

    @export
    def transfer(amount: float, to: str):
        assert amount > 0, 'Cannot send negative balances!'

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
    def transfer_from(amount: float, to: str, main_account: str):
        assert amount > 0, 'Cannot send negative balances!'

        sender = ctx.caller

        assert balances[main_account, sender] >= amount, 'Not enough Token approved to send! You have {} and are trying to spend {}'.format(balances[main_account, sender], amount)
        assert balances[main_account] >= amount, 'Not enough coins to send!'

        balances[main_account, sender] -= amount
        balances[main_account] -= amount

        balances[to] += amount

def dex() :
    # Illegal use of a builtin
    # import time
    I = importlib

    # Enforceable interface
    token_interface = [
        I.Func('transfer', args=('amount', 'to')),
        # I.Func('balance_of', args=('account')),
        I.Func('allowance', args=('owner', 'spender')),
        I.Func('approve', args=('amount', 'to')),
        I.Func('transfer_from', args=('amount', 'to', 'main_account'))
    ]

    pairs = Hash()

    # From UniV2Pair.sol
    def update(tau, token, tau_balance, token_balance, tau_reserve_last, token_reserve_last):
        # block_ts = time.time()
        # time_elapsed = block_ts - pairs[tau.name, token.name, 'block_ts_last']

        # if time_elapsed > 0 and tau_reserve_last != 0 and token_reserve_last != 0 :
        #     TODO - Calculate price_cumulative_last
        #     Need time.time() to calculate price_cumulative_last
        #     pairs[tau.token_name(), token.token_name(), 'tau_price_cumulative_last'] = int(pairs[tau.name, token.name, 'token_reserve'] / pairs[tau.name, token.name, 'tau_reserve']) * time_elapsed
        #     pairs[tau.token_name(), token.token_name(), 'token_price_cumulative_last'] = int(pairs[tau.name, token.name, 'tau_reserve'] / pairs[tau.name, token.name, 'token_reserve']) * time_elapsed

        pairs[tau.token_name(), token.token_name(), 'tau_reserve'] = tau_balance
        pairs[tau.token_name(), token.token_name(), 'token_reserve'] = token_balance
        # pairs[tau.token_name(), token.token_name(), 'block_ts_last'] = block_ts

    @construct
    def seed():
        pairs['count'] = 0

    # Simple getter
    @export
    def get_length_pairs():
        return pairs['count']

    @export
    def get_reserves(tau_contract:str, token_contract:str):
        return pairs[tau_contract, token_contract, 'tau_reserve'], \
                pairs[tau_contract, token_contract, 'token_reserve']

    @export
    def create_pair(tau_contract: str, token_contract: str, tau_amount: int, token_amount: int):
        assert token_amount > 0
        assert tau_amount > 0

        # Make sure that what is imported is actually a valid token
        tau = I.import_module(tau_contract)
        assert I.enforce_interface(tau, token_interface), 'Tau contract does not meet the required interface'

        token = I.import_module(token_contract)
        assert I.enforce_interface(token, token_interface), 'Token contract does not meet the required interface'

        assert tau_contract != token_contract
        assert pairs[tau_contract, token_contract] is None, 'Market already exists!'

        # 1 - This contract will own all amounts sent to it
        tau.transfer(tau_amount, ctx.this)
        token.transfer(token_amount, ctx.this)

        # I'm assuming registry of [ctx.this,ctx.investor,amount] is done via LP
        update(
            tau,
            token,
            tau.balance_of(ctx.this),
            token.balance_of(ctx.this),
            pairs[tau.token_name(), token.token_name(), 'tau_reserve'],
            pairs[tau.token_name(), token.token_name(), 'token_reserve']
        )

        pairs['count'] += 1

        return ctx.caller, ctx.signer, ctx.this

class MyTestCase(TestCase):

    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        # Currently mocking Lamdem functionality w/ dex_token vs. dealing with currency.py
        self.client.submit(tau, 'lamden', constructor_args={
            's_name': 'lamden',
            's_symbol': 'TAU',
            'vk': 'sys'
        })

        self.client.submit(eth, 'ethereum', constructor_args={
            's_name': 'ethereum',
            's_symbol': 'ETH',
            'vk': 'sys'
        })

        self.client.submit(dex)

    def test_step1_token_interfaces(self):
        # Get 2 token contracts
        token0 = self.client.get_contract('lamden')
        token1 = self.client.get_contract('ethereum')

        # get balances
        self.assertEqual(token0.token_name(), 'lamden')
        self.assertEqual(token0.token_symbol(), 'TAU')
        self.assertEqual(token0.quick_read('balances', 'sys'), 100)
        self.assertEqual(token0.balance_of(account='sys'), 100)

        self.assertEqual(token1.token_name(), 'ethereum')
        self.assertEqual(token1.token_symbol(), 'ETH')
        self.assertEqual(token1.quick_read('balances', 'sys'), 100)
        self.assertEqual(token1.balance_of(account = 'sys'), 100)

    def test_step2_dex_pair(self):
        token0 = self.client.get_contract('lamden')
        token1 = self.client.get_contract('ethereum')
        dex = self.client.get_contract('dex')

        n_pairs_before = dex.get_length_pairs()

        caller, signer, this = dex.create_pair(
            tau_contract = 'lamden',
            token_contract = 'ethereum',
            tau_amount= 50,
            token_amount = 50
        )

        self.assertEqual(token0.balance_of(account='sys'), 50)
        self.assertEqual(token0.balance_of(account='dex'), 50)

        self.assertEqual(token1.balance_of(account='sys'), 50)
        self.assertEqual(token1.balance_of(account='dex'), 50)

        tau_reserve, token_reserve = dex.get_reserves(
            tau_contract = 'lamden',
            token_contract = 'ethereum'
        )
        self.assertEqual(tau_reserve, 50)
        self.assertEqual(token_reserve, 50)

        n_pairs_after = dex.get_length_pairs()
        assert n_pairs_after > n_pairs_before