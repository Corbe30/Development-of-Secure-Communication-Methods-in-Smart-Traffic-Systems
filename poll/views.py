import datetime
import random
import socket
import tracemalloc
import pickle

from django.contrib.admin.forms import AuthenticationForm
from django.shortcuts import redirect, render
from . import models
from .merkleTree import merkleTree
from .resources import *
from .watcher import loadValidatedCars
from hashlib import sha512, sha256

resultCalculated = False

# CREATE VOTE
def create(request, pk):
    voter = models.Car.objects.filter(public_key_n=request.POST.get('privateKey_n'))[0]

    prevTime = 0
    prevTimes = models.Vote.objects.filter(voter_public_key_n = voter.public_key_n).order_by('-timestamp')
    if(len(prevTimes) != 0):
        prevTime = prevTimes[0].timestamp
    timeElapsed = datetime.datetime.now().timestamp() - prevTime

    if request.method == 'POST' and timeElapsed > minTimeForVoting: # also add check for geolocation??
        vote = pk
        priv_key = {'n': int(request.POST.get('privateKey_n')), 'd':int(request.POST.get('privateKey_d'))}
        pub_key = {'n':int(voter.public_key_n), 'e':int(voter.public_key_e)}

        # Create ballot as string vector
        timestamp = datetime.datetime.now().timestamp()
        ballot = "{}|{}".format(vote, timestamp)
        h = int.from_bytes(sha512(ballot.encode()).digest(), byteorder='big')
        signature = pow(h, priv_key['d'], priv_key['n'])

        hfromSignature = pow(signature, pub_key['e'], pub_key['n'])

        if(hfromSignature == h):
            status = 'Vote done successfully'
            SmartContractToWithdraw(pk, voter, timestamp)
            SmartContractForResult()
            error = False
        else:
            status = 'Authentication Error'
            error = True
        context = {
            'ballot': ballot,
            'signature': signature,
            'status': status,
            'error': error,
        }
        print(error)
        if not error:
            return render(request, 'poll/status.html', context)

    return render(request, 'poll/failure.html', context)

prev_hash = '0' * 64

# GENERATE BLOCK FOR EACH TRANSACTION
def generateBlock():
    tracemalloc.start()
    if (len(models.Vote.objects.all()) % 1 == 0):
        global prev_hash
        transactions = models.Vote.objects.order_by('block_id').reverse()
        transactions = list(transactions)[:1]
        block_id = transactions[0].block_id

        str_transactions = [str(x) for x in transactions]

        merkle_tree = merkleTree.merkleTree()
        merkle_tree.makeTreeFromArray(str_transactions)
        merkle_hash = merkle_tree.calculateMerkleRoot()

        nonce = 0
        timestamp = datetime.datetime.now().timestamp()

        while True:
            self_hash = sha256('{}{}{}{}'.format(prev_hash, merkle_hash, nonce, timestamp).encode()).hexdigest()
            if self_hash[0] == '0':
                break
            nonce += 1
        
        block = models.Block(id=block_id,prev_hash=prev_hash,self_hash=self_hash,merkle_hash=merkle_hash,nonce=nonce,timestamp=timestamp)
        prev_hash = self_hash
        block.save()
        print('Block {} has been mined'.format(block_id))
        print(tracemalloc.get_traced_memory())

def retDate(v):
    v.timestamp = datetime.datetime.fromtimestamp(v.timestamp)
    return v

# ------------------------------------------------------------------------ #
# DISPLAY UI
# ------------------------------------------------------------------------ #

# CREATE-EVENT PAGE UI
def createEvent(request):
    if request.method == 'POST':
        # loadValidatedCars()
        publickey_n = request.POST.get('privateKey_n')
        publickey_d = request.POST.get('privateKey_d')
        voter = models.Car.objects.filter(public_key_n = publickey_n)[0]
        publickey_e = voter.public_key_e
        
        priv_key = {'n': int(publickey_n), 'd':int(publickey_d)}
        pub_key = {'n':int(publickey_n), 'e':int(publickey_e)}

        timestamp = datetime.datetime.now().timestamp()
        ballot = "{}|{}".format(vote, timestamp)
        h = int.from_bytes(sha512(ballot.encode()).digest(), byteorder='big')
        signature = pow(h, priv_key['d'], priv_key['n'])

        hfromSignature = pow(signature, pub_key['e'], pub_key['n'])

        if hfromSignature == h:
            eventName = request.POST.get("eventName")
            myEvent1 = models.Event(eventID=0,occurance="hasOccured",eventName=eventName,count=0.0, creator_public_key_n=publickey_n)
            myEvent2 = models.Event(eventID=1,occurance="hasNotOccured",eventName=eventName,count=0.0, creator_public_key_n=publickey_n)
            myEvent1.save()
            myEvent2.save()
            return redirect("vote")
    
    else:
        return render(request, 'poll/createevent.html')

# HOME PAGE UI
def home(request):
    return render(request, 'poll/home.html')

# VOTE PAGE UI
def vote(request):
    events = models.Event.objects.all()
    context = {'events': events}
    return render(request, 'poll/vote.html', context)

# LOGIN PAGE UI
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            return redirect('vote')
    else:  
        form = AuthenticationForm()
    return render(request, 'poll/login.html/')

# VERIFY WEBPAGE UI
def verify(request):
    if request.method == 'GET':
        verification = ''
        tampered_block_list = verifyVotes()
        votes = []
        if tampered_block_list:
            verification = 'Verification Failed. Following blocks have been tampered --> {}.\
                The authority will resolve the issue'.format(tampered_block_list)
            error = True
        else:
            verification = 'Verification successful. All votes are intact!'
            error = False
            votes = models.Vote.objects.order_by('timestamp')
            votes = [retDate(x) for x in votes]
            
        context = {'verification':verification, 'error':error, 'votes':votes}
        return render(request, 'poll/verification.html', context)

# RESULT PAGE UI
def result(request):
    if request.method == "GET":
        voteVerification = verifyVotes()
        if len(voteVerification):
                return render(request, 'poll/verification.html', {'verification':"Verification failed.\
                Votes have been tampered in following blocks --> {}. The authority \
                    will resolve the issue".format(voteVerification), 'error':True})

        context = {"verdict":models.Event.objects.order_by('-count')[0]}
        return render(request, 'poll/results.html', context)


# ------------------------------------------------------------------------ #
# VERIFICATION OF VOTES
# ------------------------------------------------------------------------ #
def verifyVotes():
    if(verifyTampering()):
        return "tampered"
    
    if(verifyStake()):
        return "Stake less than 10%"

    if(verifyDoubleVoting()):
        return "Double Voting detected"

    return []

def verifyTampering():
    block_count = models.Block.objects.count()
    tampered_block_list = []
    for i in range (1, block_count+1):
        try:
            block = models.Block.objects.get(id=i)
        except:
            return "tampered"
        transactions = models.Vote.objects.filter(block_id=i)
        str_transactions = [str(x) for x in transactions]

        merkle_tree = merkleTree.merkleTree()
        merkle_tree.makeTreeFromArray(str_transactions)
        merkle_tree.calculateMerkleRoot()

        if (block.merkle_hash == merkle_tree.getMerkleRoot()):
            continue
        else:
            print(block.merkle_hash)
            print(merkle_tree.getMerkleRoot())
            tampered_block_list.append(i)
        
    return tampered_block_list

def verifyStake():
    votes = models.Vote.objects.all()
    lastVote = votes.order_by('-timestamp')[0]

    reputation = models.Car.objects.filter(public_key_n=lastVote.voter_public_key_n)[0].reputation
    if(abs(lastVote.transaction*100)/reputation < 11):
        return "Stake less than 10%"
    
    return []

def verifyDoubleVoting():
    votes = models.Vote.objects.all()
    lastVote = votes.order_by('-timestamp')[0]

    for vote in votes:
        if(vote.voter_public_key_n == lastVote.voter_public_key_n and vote.location == lastVote.location):
            if(lastVote.timestamp == vote.timestamp):
                continue
            if(lastVote.timestamp - vote.timestamp < minTimeForVoting):
                return "double voting found"
    
    return []


# ------------------------------------------------------------------------ #
# SMART CONTRACTS
# ------------------------------------------------------------------------ #
def SmartContractToWithdraw(pk, voter, timestamp):
    lenVoteList = len(models.Vote.objects.all())
    block_id = lenVoteList + 1

    new_vote = models.Vote(vote=pk)
    new_vote.block_id = block_id
    new_vote.voter_public_key_n = voter.public_key_n
    new_vote.timestamp = timestamp
    new_vote.location = "28.629926810308053, 77.372044875702"
    new_vote.transaction = (-10.0/100) * voter.reputation
    new_vote.save()

    voter.reputation = max(0.0, (90.0/100) * voter.reputation)
    voter.save()

    status = 'Vote done successfully'
    generateBlock()


def SmartContractForResult():
    noOfVotes = len(models.Vote.objects.all())
    if(noOfVotes % vehicleCap == 0):

        # calculate verdict
        list_of_votes = models.Vote.objects.all().order_by('-timestamp')
        list_of_votes = list_of_votes[:vehicleCap]
        for vote in list_of_votes:
            event = models.Event.objects.filter(eventID=vote.vote)[0]
            voter = models.Car.objects.filter(public_key_n=vote.voter_public_key_n)[0]
            if(voter.reputation > 0.2):
                event.count += 1*voter.reputation
                event.save()
            
        verdict = models.Event.objects.order_by('count').reverse()[0]

        # filter votes for and against the poll
        for vote in list_of_votes:
            voters = models.Car.objects.filter(public_key_n=vote.voter_public_key_n)
            if(len(voters) != 0):
                voter = models.Car.objects.filter(public_key_n=vote.voter_public_key_n)[0]
                if(vote.vote == verdict.eventID):
                    if(voter.public_key_n == verdict.creator_public_key_n):
                        SmartContractToAward(voter, True)
                    else:
                        SmartContractToAward(voter, False)

def SmartContractToAward(voter, isCreator):
    lenVoteList = len(models.Vote.objects.all())
    block_id = lenVoteList + 1

    new_vote = models.Vote(vote=2)
    new_vote.block_id = block_id
    new_vote.voter_public_key_n = voter.public_key_n
    new_vote.location = "28.629926810308053, 77.372044875702"
    new_vote.timestamp = datetime.datetime.now().timestamp()

    
    if(not isCreator):
        new_vote.transaction = (48.0/100) * voter.reputation
        voter.reputation = max(0.0, (148.0/100) * voter.reputation)
    else:
        new_vote.transaction = (55.0/100) * voter.reputation
        voter.reputation = max(0.0, (155.0/100) * voter.reputation)
    
    voter.save()
    new_vote.save()
    
    generateBlock()


# ------------------------------------------------------------------------ #
# SHARING DATA WITH OTHER NODES
# ------------------------------------------------------------------------ #

def sendMessage(port, message, option):
    s = socket.socket()
    s.connect(('localhost', port))

    temp = [option, message]
    temp = pickle.dumps(temp)

    s.send(temp)

def receiveMessage(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(3)
    addr = 0
    while True:
        if(addr == 0):
            c, addr = s.accept()
            data = (c.recv(4096))

        if(addr != 0):
            break
    
    data = pickle.loads(data)
    if(data[0] == 'blockchain&ledger'):
        return data[1]

def shareBlockchainLedger():
    blockchain = models.Block.objects.all()
    ledger = models.Vote.objects.all()
    event = models.Event.objects.all()
    sendMessage(1000, [blockchain, ledger, event], 'blockchain&ledger')

def receiveBlockchainLedger():
    [blockchain, ledger, event] = receiveMessage(1000)
    blockchain.objects.all().delete()
    models.Block.objects.all().delete()
    models.Event.objects.all().delete()
    models.Vote.objects.all().delete()

    blockchain.save()
    ledger.save()
    event.save()