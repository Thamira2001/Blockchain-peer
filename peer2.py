#Name : Thamira Randeniya
#Course: COMP 3010
#Assignment :#3
#Professor : Dr. Sarah Rouhani
#this program creates a peer for the p2p network and does concensus to find the longest chain and tries to create sync with that chain by requesting blocks


import socket
import json
import threading
import uuid
import time
import hashlib
import sys
import ast
import hashlib
import time

class Block:
    def __init__(self, previous_hash, miner_name, messages, nonce, difficulty=8):
        self.previous_hash = previous_hash
        self.miner_name = miner_name
        self.messages = messages[:10]  #limits the messages to 10
        self.timestamp = time.time()
        self.nonce = nonce
        #set to 8
        self.difficulty = difficulty
        self.hash_CAL()

    #function calculates the hash of the block using hashlib
    def hash_CAL(self):
        data =hashlib.sha256()
        data.update(self.previous_hash.encode())
        data.update(self.miner_name.encode())

        for i in range(0,len(self.messages) -1):
            data.update(self.messages[i].encode())
        
        data.update(int(self.timestamp).to_bytes(8,'big'))
        data.update(self.nonce.encode())
        data.hexdigest()

        self.hash=data
        
    def to_dict(self):
        return {
            "previous_hash": self.previous_hash,
            "miner_name": self.miner_name,
            "messages": self.messages,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = []

    def add_block(self, block):
        if len(self.chain) > 0:
            block.previous_hash = self.chain[len(self.chain)-1].hash
        self.chain.append(block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.hash_CAL():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True


class Peer:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.portS=8376
        self.id = str(uuid.uuid4())
        self.syncedPeer=[]
        self.peers = {}
        self.peerHeight ={}
        self.peerHash = {}
        self.gossipList={}
        self.heightHashCombo = {}
        self.mostAgreedUpon_height=None#default set to None
        self.mostAgreedUpon_hash=None#deault set to None
        self.tracked_peers = []
        self.blockchain = Blockchain()
        self.well_known_host="130.179.28.37"
        self.well_known_port=8999

        # Constants
        self.MAX_TRACKED_PEERS = 3
        self.GOSSIP_INTERVAL = 30  # seconds

      
    #send a gossip message to the three peers im tracking every thirty seconds
    def gossip_periodically(self):
        while True:
            self.gossip()
            
            time.sleep(self.GOSSIP_INTERVAL)

    def send_message(self, message, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.sendto(message.encode('utf-8'), (host, port))

            s.close()

    def receive_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            try:
                while True:
                    data, addr = s.recvfrom(1024)
                    message = json.loads(data.decode('utf-8'))
                    self.handle_message(message, addr[0], addr[1])
            finally:
                s.close()
                

    def handle_message(self, message, origin_host, origin_port):

        message_type = message.get('type')
    
        if message_type == 'GOSSIP':
            self.handle_gossip(message)
        elif message_type == 'GOSSIP_REPLY':
            print(f"NEED TO REPLY TO A GOSSIP")
            self.handle_gossip_reply(message)
        elif message_type == 'GET_BLOCK':
            self.handle_get_block(message, origin_host, origin_port)
        elif message_type =='GET_BLOCK_REPLY':
            print(f"GOT THE DAMN BLOCK REPLY")
            self.handle_get_block_reply(message)
        elif message_type == 'ANNOUNCE':
            self.handle_announce(message)
        elif message_type == 'STATS':
            self.handle_stats(origin_host, origin_port)
        elif message_type == 'STATS_REPLY':
            print(f"BOOOO YEA GOT THE STATS REPLY ")
            self.handle_stats_reply(message, origin_host, origin_port)
        elif message_type == 'CONSENSUS':
            self.consensus()

    

    def handle_gossip(self, message):

        if message not in self.tracked_peers:
            if len(self.tracked_peers) < self.MAX_TRACKED_PEERS:
                self.tracked_peers.append(message)

        key = message['id']
        if key not in self.gossipList:
            self.gossipList[message['id']]=message
            
            reply_message = {
                "type": "GOSSIP_REPLY",
                "host": self.host,
                "port": self.port,
                "name": "Thamira Randeniya"
            }

            print(f"Length of list is : {len(self.gossipList)}")
            print(f" host is this  :{message['host']} port is this : {message['port']}")
            self.send_message(json.dumps(reply_message), message['host'], message['port'])
        


        
        

    def handle_gossip_reply(self, message):
        key_p = message['name']
        print(f"key is {key_p}")
        if key_p not in self.peers and len(self.peers) < self.MAX_TRACKED_PEERS:
            self.peers[key_p]=message






        

    def handle_get_block(self, message, origin_host, origin_port):
        height = message.get('height', None)
        if height is not None and 0 <= height < len(self.blockchain.chain):
            block = self.blockchain.chain[height]
            reply_message = {
                "type"   : "GET_BLOCK_REPLY",
                "hash": block.hash,
                "height": block.height,
                "messages": block.messages,
                "minedBy": block.miner_name,
                "minedBy": block.nonce,
                "timestamp": block.timestamp
            }
        else:
            reply_message = {
                "type"   : "GET_BLOCK_REPLY",
                "hash": None,
                "height": None,
                "messages": None,
                "minedBy": None,
                "minedBy": None,
                "timestamp": None
            }
        self.send_message(json.dumps(reply_message), origin_host, origin_port)

    def handle_get_block_reply(self, message):
        
        newBlock=Block(message['hash'],message['minedBy'],message['messages'],message['nonce'])

        self.blockchain.add_block(newBlock)

        
            
    


    def handle_announce(self, message):
        # Add new block to the chain after verifying its hash
        new_block = Block(
            message['hash'],
            message['minedBy'],
            message['messages'],
            message['nonce']
        )
        if new_block.hash == message['hash']:
            self.blockchain.add_block(new_block)
    
    

    def handle_stats(self, origin_host, origin_port):

        if len(self.blockchain.chain) == 0:
            msg ={
            "type": "STATS_REPLY",
            "height":"0",
            "hash": "doing conensus"
            }
            self.send_message(json.dumps(msg), origin_host, origin_port)
        else:
            stats_message = {
                "type": "STATS_REPLY",
                "height": len(self.blockchain.chain) - 1,  # Subtract 1 as height is 0-based
                "hash": str(self.blockchain.chain[len(self.blockchain.chain) - 1].hash)
            }
            self.send_message(json.dumps(stats_message), origin_host, origin_port)

    def handle_stats_reply(self, message, origin_host, origin_port):
        print(f"inside managaing stats reply !")
        if message['height'] != None and message['hash']!=None :
            h = message['height']
            hash = message['hash']
        else:
            print(f"Invalid height or hash")
            return
        
       
        
        if isinstance(h,int):
            if (self.mostAgreedUpon_height is None) and (self.mostAgreedUpon_hash is None):
                #adding to the dictionary containing height nad hashcombo from stat reply
                self.heightHashCombo[hash]=h 

                #adding to the list of host and ports of peers that sent stat replies with the height, hash tuple as a key of that peer's host and port tuple 
                self.peerHeight[(h, hash)]=(origin_host,origin_port)

    
                
                print(f"list of height and hashCombos : {self.heightHashCombo}")
            
        else:
            print(f" FOUND AN invalid height!")
        

    def send_get_block_request(self, block_no, host, port):
        get_block_msg = {
            "type": "GET_BLOCK",
            "height": block_no
        }

        self.send_message(json.dumps(get_block_msg), host, port)
        print(f"sent by me : {get_block_msg}")

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        receive_thread.join()
        # time.sleep(5)

    def get_Those_blocks(self, host, port, height):
        for i in range (0,height):
            hostO, portO =self.syncedPeer[0] 
            print(f"chosen host is {hostO} and chosen port is {portO} and is {self.mostAgreedUpon_height} is {self.mostAgreedUpon_hash}")
            self.send_get_block_request(i,host, port)


    def send_stat_request(self):
        print(f"\n SENDING STAT REQUESTSSSS!!!\n\n")
        request_stats_msg={
            "type":"STATS"
        }

        time.sleep(8)    
        for peer in self.peers.values(): 
            self.send_message(json.dumps(request_stats_msg),peer['host'], peer['port'] )
            print(f"sent by me : {request_stats_msg} to {peer['host']}, {peer['port']}")

        

    def consensus(self):
        # Perform consensus logic to find the longest chain
        # Request STATS from everyone and choose the most agreed-upon chain

        print(f"DOING CONCENSUS")
        self.mostAgreedUpon_hash =None
        self.mostAgreedUpon_height=None

        self.send_stat_request()

        time.sleep(20)#sleep to allow my peer to get stat replies
        
        longestChain = max(self.heightHashCombo.values())
        self.mostAgreedUpon_height = longestChain

        print(f"longest chain height is {longestChain}")

        listOfHash =[]

        for key, value  in self.heightHashCombo.items():
            if value == self.mostAgreedUpon_height:
                listOfHash.append(key)

        frequency ={}

        for i in listOfHash:
            if i in frequency:
                frequency[i]+=1
            else:
                frequency[i]=1

        self.mostAgreedUpon_hash=max(frequency,key=frequency.get)

        with open('example.txt', 'a') as file:
            file.write(f"ATTENTION: MOST AGREED UPON HEIGHT IS {self.mostAgreedUpon_height} and HASH is {self.mostAgreedUpon_hash}\n")
            file.close()
        
        print(f"ATTENTION: MOST AGREED UPON HEIGHT IS {self.mostAgreedUpon_height} and HASH is {self.mostAgreedUpon_hash}")

        #adds all the synced peers into a list 
        for t in self.peerHeight:
            if (self.mostAgreedUpon_height, self.mostAgreedUpon_hash) == t:
                self.syncedPeer.append(self.peerHeight[t])

        with open('example.txt', 'a') as file:
            file.write(f"ATTENTION THIS IS THE LIST OF PEERS IM IN SYNC WITH : {self.syncedPeer}\n\n")
            file.close()
        
        print(f"ATTENTION THIS IS THE LIST OF PEERS IM IN SYNC WITH : {self.syncedPeer}")

        
        
        print(f"DONE WITH CONCENSUS!")

        hostO, portO =self.syncedPeer[0]
        self.get_Those_blocks(hostO, portO, self.mostAgreedUpon_height)

        duration =10 
        endTime = time.time() + duration 

        
       

    def gossip(self):
        
        self.gossipList = {}

        # Implement logic to gossip about your peer to the network
        gossip_message = {
                "type": "GOSSIP",
                "host": self.host,
                "port": self.port,
                "id": self.id,
                "name": "Thamira Randeniya"
                }
        
        for myPeer in self.tracked_peers:
            self.send_message(json.dumps(gossip_message), myPeer['host'], myPeer['port'])

        
    def join_network(self):
        
        gossip_message ={
                "type": "GOSSIP",
                "host": self.host,
                "port": self.port,
                "id": self.id,
                "name": "Thamira Randeniya"
        }
        self.send_message(json.dumps(gossip_message), self.well_known_host, self.well_known_port)

        print(f"sent by me to join network {gossip_message} to {self.well_known_host} on {self.well_known_port}")

       

        while len(self.peers) == 0 :
            #do nothing
            time.sleep(10) 
            #"waiting for peers to be poppulated"
        gossip_thread =threading.Thread(target=self.gossip_periodically)
        gossip_thread.start()

        
        
        self.consensus()

        

        

       

# Example Usage:
if __name__ == "__main__":
    # Replace 'localhost' and 8888 with your actual host and port
    hostName=socket.gethostname()
    host=socket.gethostbyname(hostName)
    port=8377

    peer = Peer(host, port)

    receive_thread = threading.Thread(target=peer.receive_messages)
    receive_thread.start()

    
    print(f"host: {host}, port:{8377}")
    peer.join_network()

    
