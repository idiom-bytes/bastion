from unittest import TestCase
from contracting.client import ContractingClient

def dex() :

    # Simple getter
    @export
    def get_length_pairs():
        arr = [1,2]
        return len(arr)

class MyTestCase(TestCase):

    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        self.client.submit(dex, 'dex')

    def test_dex_function(self):
        dex = self.client.get_contract('dex')

        self.assertEqual(dex.get_length_pairs(), 2)