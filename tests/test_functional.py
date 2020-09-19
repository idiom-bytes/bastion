from unittest import TestCase

from contracting.client import ContractingClient
from dex_token import dex_token
from dex import dex

class MyTestCase(TestCase):

    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        # Currently mocking Lamdem functionality w/ dex_token vs. dealing with currency.py
        self.client.submit(dex_token, 'Lamden', constructor_args={
            'vk': 'actor1',
            's_symbol': 'TAU'
        })

        self.client.submit(dex_token, 'Ethereum', constructor_args={
            'vk': 'actor1',
            's_symbol': 'ETH'
        })

        self.client.submit(dex_token, 'Antiample', constructor_args={
            'vk': 'actor1',
            's_symbol': 'XAMP'
        })

        self.client.submit(dex)

    def test_step1_assign_tokens(self):
        # Get 2 token contracts
        token0 = self.client.get_contract('Lamden')
        token1 = self.client.get_contract('Ethereum')

        # get balances
        self.assertEqual(token0.name, 'Lamden')
        self.assertEqual(token0.symbol(), 'TAU')
        self.assertEqual(token0.quick_read('balances', 'actor1'), 100)

        self.assertEqual(token1.name, 'Ethereum')
        self.assertEqual(token1.symbol(), 'ETH')
        self.assertEqual(token1.quick_read('balances', 'actor1'), 100)

    def test_step2_create_pair(self):
        dex = self.client.get_contract('dex')

        n_pairs_before = dex.get_length_pairs()

        dex.create_pair(
            tau_contract = 'Tau',
            token_contract = 'Ethereum',
            tau_amount= 50,
            token_amount = 50
        )
        dex.create_pair(
            tau_contract = 'Tau',
            token_contract = 'Antiample',
            tau_amount= 50,
            token_amount = 50
        )

        n_pairs_after = dex.get_length_pairs()

        assert n_pairs_after > n_pairs_before