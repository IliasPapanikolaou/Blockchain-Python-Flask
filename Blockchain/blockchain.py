import datetime
import hashlib
import json
import http
from flask import Flask, jsonify


# Part 1 - Building a Blockchain
class Blockchain:
    def __init__(self):
        # init a list
        self.chain = []
        # Genesis block
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        # dictionary
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    def get_previous_block(self):
        # get the last block of the chain (-1) is the last index of the chain
        return self.chain[-1]

    # Proof of Work is the number or piece of data that the miners have to find
    # in order to mine a new block (hard to find, easy to verify)
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # regex of SHA-256 hexadecimal hash and its length [A-Fa-F0-9]{64}
            # the formula inside hash_operation hash is arbitrarily defined by the programmer
            # encode puts a 'b' before the result - ex: if result is '5' then encode will result b'5'
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            # hash_operations outputs a 64 length sha256 hash
            # print(hash_operation)
            # if hash operation starts with four zeros '0000': 0 to 4 indexes in array, last index is excluded
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    # Hash method will take the block as input and will return its sha256 hash
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # Functions that will check if everything is right in the blockchain
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # check1: If each block of blockchain has correct proof of work
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # check2: If the previous_hash of each block equals to the previous block's hash
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            # check if starts with four leading zeroes '0000'
            if hash_operation[:4] != '0000':
                return False
            # update previous_block and increment by 1
            previous_block = block
            block_index += 1
        return True


# Part 2 - Mining our Blockchain
# Create a Web App
app = Flask(__name__)

# For making the server publicly available use app.run(host='0.0.0.0', port=5000)
if __name__ == '__main__':
    app.run()


# Create a Blockchain
blockchain = Blockchain()


# Mining a new block
# Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    # get previous proof (nonce)
    proof = blockchain.proof_of_work(previous_proof)
    # get previous_hash
    previous_hash = blockchain.hash(previous_block)
    # create new block
    block = blockchain.create_block(proof, previous_hash)
    # response as dictionary
    response = {'message': 'Congratulations you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), http.HTTPStatus.OK  # Http Status: 200


# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), http.HTTPStatus.OK  # Http Status: 200


# Check if the Blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_blockchain_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_blockchain_valid:
        response = {'message': 'The blockchain is valid.'}
    else:
        response = {'message:' 'The blockchain is invalid.'}
    return jsonify(response), 200