from unittest import TestCase

from contracting.client import ContractingClient
from dex import dex

class MyTestCase(TestCase):

    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        self.client.submit(dex)

    def test_step2_create_pair(self):
        dex = self.client.get_contract('dex')

        assert dex.get_length_pairs() == 2