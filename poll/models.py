from django.db import models
from uuid import uuid4
from datetime import datetime
from django import forms
# Create your models here.

def get_time():
    return datetime.now().timestamp()

class Event(models.Model):
    eventID = models.IntegerField(primary_key=True, default=0)
    occurance = models.CharField(max_length=100)
    eventName = models.CharField(max_length=100)
    location = models.CharField(max_length=320)
    count = models.FloatField(default=0.0)
    creator_public_key_n = models.CharField(max_length=320)

class Car(models.Model):
    username = models.CharField(max_length=30)
    public_key_n = models.CharField(max_length=320)
    public_key_e = models.IntegerField(default=65537)
    reputation = models.FloatField(default=0.5)
    #has_voted = models.BooleanField(default=False)

class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    voter_public_key_n = models.CharField(max_length=320)
    vote = models.IntegerField(default=2)
    timestamp = models.FloatField(default=get_time)
    block_id = models.IntegerField(null=True)
    transaction = models.FloatField(default=0.0)
    location = models.CharField(max_length=320)
    

    def __str__(self):
        return "{}|{}|{}".format(self.id, self.vote, self.timestamp)

class Block(models.Model):
    id = models.IntegerField(primary_key=True, default=0)
    prev_hash = models.CharField(max_length=64, blank=True)
    merkle_hash = models.CharField(max_length=64, blank=True)
    self_hash = models.CharField(max_length=64, blank=True)
    nonce = models.IntegerField(null=True)
    timestamp = models.FloatField(default=get_time)

    def __str__(self):
        return str(self.self_hash)

