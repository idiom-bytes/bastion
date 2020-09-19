from unittest import TestCase
from contracting.client import ContractingClient

def dex_sample() :
    symbol = Variable()

    # Cannot set breakpoint in @construct
    @construct
    def seed(s_symbol: str):
        symbol.set(s_symbol)

    @export
    def symbol():
        return symbol.get()

# TODO - This tests shows that submitting contract inline, is working fine.
# However, this method is less desirable due to copy pasta
class MyTestCase(TestCase):

    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        self.client.submit(dex_sample, 'dex_sample', constructor_args={
            's_symbol': 'TAU'
        })

    def test_create_pair(self):
        dex_sample = self.client.get_contract('dex_sample')

        # We can verify that an inline import of dex_sample works
        self.assertEqual(dex_sample.symbol(), 'TAU')