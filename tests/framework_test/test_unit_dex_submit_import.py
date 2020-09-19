from unittest import TestCase
from contracting.client import ContractingClient
from dex_sample import dex_sample

# TODO - This test should be compared to test_unit_dex_token_submit_import.py
class MyTestCase(TestCase):

    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        self.client.submit(dex_sample, 'dex_sample', constructor_args={
            's_symbol': 'TAU'
        })

    def test_create_pair(self):
        dex_sample = self.client.get_contract('dex_sample')

        # Test that the symbol method rases an AttributeError
        # To summarize - Importing doesn't always work
        self.assertRaises(
            AttributeError,
            lambda: dex_sample.symbol()
        )