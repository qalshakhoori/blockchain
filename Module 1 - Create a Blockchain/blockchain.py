import datetime
import hashlib
import json
from os import system
from flask import Flask, jsonify

# Part 1: Building a Blockchain


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }

        self.chain.append(block)
        return block

    def get_previuos_block(self):
        return self.chain[-1]  # get last block of the blockchain

# Part 2 - Mining our blockchain
