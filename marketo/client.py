'''
Created on Aug 5, 2011

@author: seant
'''

from rfc3339 import rfc3339
from suds.cache import FileCache
from suds.client import Client
from suds.plugin import MessagePlugin
from suds.sax.element import Element
import hmac
import hashlib
import logging
import os
import datetime
import suds.sudsobject


soapDateTime = rfc3339

def sign(secret, message):
    digest = hmac.new(secret, message, hashlib.sha1)
    return digest.hexdigest().lower()

# From Marketo example"
userid="bigcorp1_461839624B16E06BA2D663"
secret="899756834129871744AAEE88DDCC77CDEEDEC1AAAD66"
timestamp="2010-04-09T14:04:54-07:00"
# Ensure that our signing method works, or don't even load.
assert sign(secret,timestamp+userid)=="ffbff4d4bef354807481e66dc7540f7890523a87", "Marketo signing method failed sanity test"

# Really tacky envelope manipulation to get SUDS request acceptable to Marketo server
# TODO: an XMl/SOAP guru should do this at the DOM level, or figure out why it's necessary
front = """<SOAP-ENV:Envelope xmlns:SOAP-ENV = "http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1 = "http://www.marketo.com/mktows/" """
replacements = [("ns1:Body","SOAP-ENV:Body"),("ns0:","ns1:"),]
def patchEnvelope(envelope):
    parts = envelope.split(">")
    parts[1] = front
    envelope = ">".join(parts)
    for f,t in replacements:
        envelope = envelope.replace(f,t)
    return envelope


# Marketo requires a unique authentication header (but on the up side, no login or session)
# Brute force in with a patch to the envelope, which also requires a patch to SUDS :-(
# TODO: Get patch accepted in SUDS or rewrite to use DOM level code
class MarketoSignaturePlugin(MessagePlugin):
    authfragment = """
    <SOAP-ENV:Header>
    <ns1:AuthenticationHeader>
    <mktowsUserId>%(userid)s</mktowsUserId>
    <requestSignature>%(signature)s</requestSignature>
    <requestTimestamp>%(timestamp)s</requestTimestamp>
    </ns1:AuthenticationHeader>
    </SOAP-ENV:Header>
    """
    def __init__(self, userid, secret, *args, **kwargs):
        self.userid = userid
        self.secret = secret
        self.debug = kwargs.get("debug", True)
    def sending(self, context):
        userid = self.userid
        timestamp = rfc3339(datetime.datetime.now())
        secret = self.secret
        signature = sign(secret, timestamp+userid)
        auth = self.authfragment % locals()
        envelope = context.envelope
        envelope = envelope.replace("<SOAP-ENV:Header/>", auth)
        envelope = patchEnvelope(envelope)
        if self.debug:
            with open("/tmp/envelope.txt","w") as f: f.write(envelope)
        context.envelope = envelope
        return context
    
def MarketoClientFactory(ini, **kwargs):
    import json
    with open(ini) as f:
        ini = json.loads(f.read())
    for key, item in ini.items():
        ini[key] = str(item)
    ini.update(kwargs)
    wsdl = ini["wsdl"]
    if '://' not in wsdl:
        if os.path.isfile(wsdl):
            wsdl = 'file://' + os.path.abspath(wsdl)
        cache = None # TODO: Evaluate using cache
    client = Client(wsdl, cache=cache, plugins=[MarketoSignaturePlugin(ini["userid"],ini["encryption_key"])])
    headers = {}
    client.set_options(headers=headers)
    if kwargs.has_key('proxy'):
        if kwargs['proxy'].has_key('https'):
            raise NotImplementedError('Connecting to a proxy over HTTPS not supported.')
        client.set_options(proxy=kwargs['proxy'])
    return client

