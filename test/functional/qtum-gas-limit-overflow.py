#!/usr/bin/env python3

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *
from test_framework.script import *
from test_framework.mininode import *
from test_framework.address import *
from test_framework.qtum import *
import sys
import random
import time
import io
from test_framework.qtumconfig import INITIAL_WALLET_BALANCE

class QtumGasLimitOverflowTest(BitcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 1


    def run_test(self):
        self.node = self.nodes[0]
        self.node.setmocktime(int(time.time()) - 1000000)
        self.node.generate(200 + COINBASE_MATURITY)
        unspents = [unspent for unspent in self.node.listunspent() if unspent['amount'] == Decimal(INITIAL_WALLET_BALANCE)]
        unspent = unspents.pop(0)

        tx = CTransaction()
        tx.vin = [CTxIn(COutPoint(int(unspent['txid'], 16), unspent['vout']))]
        tx.vout = [CTxOut(0, scriptPubKey=CScript([b"\x04", CScriptNum(0x10000), b"\x00", OP_CREATE])) for i in range(0x10)]
        tx = rpc_sign_transaction(self.node, tx)
        assert_raises_rpc_error(-26, "absurdly-high-fee", self.node.sendrawtransaction, bytes_to_hex_str(tx.serialize()))
        self.node.generate(1)

if __name__ == '__main__':
    QtumGasLimitOverflowTest().main()
