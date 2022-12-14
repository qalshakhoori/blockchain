# requests===2.18.4: pip install requests===2.18.4
import datetime
import hashlib
from http.client import BAD_REQUEST, CREATED, OK
import json
from uuid import uuid4
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse
import sys

# Part 1: Building a Blockchain


class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []  # initialize transactions list before minig the first bllock
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }

        self.transactions = []

        self.chain.append(block)
        return block

    def get_previuos_block(self):
        return self.chain[-1]  # get last block of the blockchain

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True, default=str).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            previous_block = block
            block_index += 1

        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })

        previous_block = self.get_previuos_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc)

    def replace_chain(self):
        netwrok = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in netwrok:
            response = requests.get(f'http://{node}/get_chain')
            if(response.status_code == 200):
                length = response.json()['length']
                chain = response.json()['chain']
                if(length > max_length and self.is_chain_valid(chain)):
                    max_length = length
                    longest_chain = chain

        if(longest_chain):
            self.chain = longest_chain
            return True


# Part 2 - Mining our blockchain
# Creating a Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

# Minig a new block


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previuos_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(
        sender=node_address, receiver='Qassim', amount=1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': list(block['transactions'])}
    print(response)
    return jsonify(response), OK

# Getting the full blockchain


@app.route('/get_chain', methods=['GET'])
def get_chain():
    respone = {'chain': blockchain.chain,
               'length': len(blockchain.chain)}
    return jsonify(respone), OK

# Check if the blockchain is valid


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if(is_valid):
        response = {'message': 'BLOCKCHAIN IS VALID', 'is_valid': True}
    else:
        response = {'message': 'BLOCKCHAIN IS NOT VALID', 'is_valid': False}
    return jsonify(response), OK

# Adding a new transaction to the Blockchain


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json(cache=False)
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', BAD_REQUEST

    index = blockchain.add_transaction(
        json['sender'], json['receiver'], json['amount'])
    response = {
        'message': f'This transaction will be added to Block {index}',
        'index': index
    }

    return jsonify(response), CREATED

# Part 3 - Decentralizing our Blockchain

# Connecting new nodes


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json(cache=False)
    print(json)
    nodes = json.get('nodes')
    if (nodes is None):
        return "No Node", BAD_REQUEST
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message': 'All the nodes are now connected. The qcoin blockchain now contains the following nodes',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), CREATED

# Replacing the chain with the longest chain if needed


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if(is_chain_replaced):
        response = {
            'message': 'The nodes had different chains so the chain was replaced by the longest chain',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'All good, the chain is the longest chain',
            'actual_chain': blockchain.chain
        }
    return jsonify(response), OK


# Running the app
port = int(sys.argv[1])
app.run(host='0.0.0.0', port=port)
