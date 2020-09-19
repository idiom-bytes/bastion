from unittest import TestCase
from contracting.client import ContractingClient

# TODO - This tests shows that submitting contract via a file string is not working.
# dex_sample.symbol() function cannot be found in attributes, inside executor.py
class MyTestCase(TestCase):

    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        with open('../../dex_sample.py') as f:
            code = f.read()
            self.client.submit(code, name='dex_sample', constructor_args={
                's_symbol': 'TAU'
            })

    def test_create_pair(self):
        dex_sample = self.client.get_contract('dex_sample')

        # Test that the symbol method rases an AttributeError
        # To summarize - Importing contract as a string doesn't load the functions as part of the contract's attribute
        self.assertRaises(
            AttributeError,
            lambda: dex_sample.symbol()
        )