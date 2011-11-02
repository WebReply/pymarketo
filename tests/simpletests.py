from marketo.client import MarketoClientFactory
import os
import sys #@UnusedImport
import time #@UnusedImport
import datetime #@UnusedImport
from pprint import pprint #@UnresolvedImport

TESTDIR = os.path.split(__file__)[0]
PACKAGEDIR = os.path.join(TESTDIR,"..")
INIFILE = os.path.join(PACKAGEDIR,"marketo.ini")
DATAFILES=["specification","listMObjects"]


# The following must be set up on your marketo account to enable tests
LEADEMAIL = "seant@webreply.com"        # Email of an internal contact
LEADLIST = "2wr-0"            # List name containing LEADEMAIL contact
SPECIALCODE = "WebReplyJobCode"           # If your leads have a custom field that can be
SPECIALVALUE= "WEBREPLY"                  # asserted for LEADEMAIL, set them here
TESTCAMPAIGN = "SOAP API Access test" # Name of test campaign that has SOAP API trigger enabled
DELETECAMPAIGN = "Delete lead" # Campaign configure to delete leads added to the campaign

# First and last names, and synthetic email addresses for new leads
# These will be added and then deleted
TESTDOMAIN="webreply.com"
TESTNAMES = [("One","Test",TESTDOMAIN),("Two","Test",TESTDOMAIN)]
TESTEMAILS = ["%s.%s@%s" % name for name in TESTNAMES]


mc = MarketoClientFactory(INIFILE)

def compareData(datafile, data):
    path = os.path.join(TESTDIR,datafile+".txt")
    return open(path).read().strip() == data.strip()

def test_data():
    "Make sure that all the test data files are present"
    assert os.path.exists(INIFILE)
    for datafile in DATAFILES:
        assert os.path.exists(os.path.join(TESTDIR,datafile+".txt"))
        
# Factory methods to build structures for arguments
def aStringArray(strings):
    asa = mc.factory.create("ArrayOfString")
    asa.stringItem = strings
    return asa

def aLeadKey(email=None,id=None):
    leadkey = mc.factory.create("LeadKey")
    if email:
        leadkey.keyType = "EMAIL"
        leadkey.keyValue = email
    elif id:
        leadkey.keyType = "IDNUM"
        leadkey.keyValue = id
    return leadkey

def aLeadKeyArray(leads):
    lka = mc.factory.create("ArrayOfLeadKey")
    lka.leadKey = leads
    return lka

def aListKey(lk, keyType = "MKTOLISTNAME"):
    listkey = mc.factory.create("ListKey")
    listkey.keyType = keyType
    listkey.keyValue = lk
    return listkey

def anAttrib(**kwargs):
    attrib = mc.factory.create("Attrib")
    for key, value in kwargs.items():
        setattr(attrib, key, value)
    return attrib

def anAttribArray(attribs):
    aa = mc.factory.create("ArrayOfAttrib")
    aa.attrib=attribs
    return aa

def anAttribute(**kwargs):
    attrib = mc.factory.create("Attribute")
    for key, value in kwargs.items():
        setattr(attrib, key, value)
    return attrib

def anAttributeArray(attributes):
    aa = mc.factory.create("ArrayOfAttribute")
    aa.attribute=attributes
    return aa

def aLeadRecord(id=None, email=None, foreignsyspersonid=None,foreignsystype=None,attributes=None):
    lr = mc.factory.create("LeadRecord")
    if id:
        lr.Id = id
    elif email:
        lr.Email = email
    elif foreignsyspersonid:
        assert foreignsystype
        lr.ForeignSysPersonId = foreignsyspersonid
        lr.ForeignSysType = foreignsystype
    if attributes:
        lr.leadAttributeList = attributes
    return lr

def aLeadRecordArray(leadrecords):
    lra = mc.factory.create("ArrayOfLeadRecord")
    lra.leadRecord = leadrecords
    return lra

# Several things come back with an attribute list that is more pleasant as a dictionary
def attrs2dict(attributelist):
    if attributelist is None:
        return {}
    attributelist = attributelist[0]
    d = dict([(attr.attrName,attr.attrValue) for attr in attributelist])
    return d
def dict2attrs(d):
    al = []
    for key, value in d.items():
        al.append(anAttribute(attrName=key,attrValue=value))
    return anAttributeArray(al)

def test_specification():
    compareData("specification", str(mc))


# As of 1.7, these are the methods 
# Untested: deleteCustomObjects(xs:string objTypeName, ArrayOfKeyList customObjKeyLists, )
# UnTested: deleteMObjects(ArrayOfMObject mObjectList, )
# Tested: describeMObject(xs:string objectName, )
# Requires having a trigger set for the campaign, from Marketo support:
# Your SOAP request is fine. In order for the getCampaignsForSource call to work, 
# you must have a "Campaign is Requested" trigger in the your campaign set to Web Service API.
# Tested: getCampaignsForSource(ReqCampSourceType source, xs:string name, xs:boolean exactName, )
# Untested: getCustomObjects(xs:string objTypeName, xs:string streamPosition, xs:int batchSize, ArrayOfAttribute customObjKeyList, ArrayOfString includeAttributes, )
# Tested: getLead(LeadKey leadKey, )
# Tested: getLeadActivity(LeadKey leadKey, ActivityTypeFilter activityFilter, StreamPosition startPosition, xs:int batchSize, )
# Tested: getLeadChanges(StreamPosition startPosition, ActivityTypeFilter activityFilter, xs:int batchSize, )
# getMObjects(xs:string type, xs:int id, Attrib externalKey, ArrayOfMObjCriteria mObjCriteriaList, ArrayOfMObjAssociation mObjAssociationList, xs:string streamPosition, )
# Tested: getMultipleLeads(xs:dateTime lastUpdatedAt, xs:string streamPosition, xs:int batchSize, ArrayOfString includeAttributes, )
# Tested: listMObjects()
# Tested: listOperation(ListOperationType listOperation, ListKey listKey, ArrayOfLeadKey listMemberList, xs:boolean strict, )
# mergeLeads(ArrayOfAttribute winningLeadKeyList, ArrayOfKeyList losingLeadKeyLists, )
# requestCampaign(ReqCampSourceType source, xs:int campaignId, ArrayOfLeadKey leadList, )
# syncCustomObjects(xs:string objTypeName, ArrayOfCustomObj customObjList, SyncOperationEnum operation, )
# Tested: syncLead(LeadRecord leadRecord, xs:boolean returnLead, xs:string marketoCookie, )
# Untested: syncMObjects(ArrayOfMObject mObjectList, SyncOperationEnum operation, )
# Tested: syncMultipleLeads(ArrayOfLeadRecord leadRecordList, xs:boolean dedupEnabled, )

# Campaign sources
# <xs:enumeration value="MKTOWS"/>
# <xs:enumeration value="SALES"/>

def test_getCampaignsForSource():
    print "Testing getCampaignsForSource"
    campaigns = mc.service.getCampaignsForSource("MKTOWS",None,False)
    resultCount = campaigns.returnCount
    campaignrecords = campaigns.campaignRecordList[0]
    assert  resultCount==len(campaignrecords), "Result count '%s' does not match campaign list '%s'" % (resultCount, len(campaigns))
    for campaign in campaignrecords:
        print campaign.id, campaign.name, campaign.description
    print



def test_getLead():
    print "Testing getLead"
    leadkey = aLeadKey(email=LEADEMAIL)
    lead = mc.service.getLead(leadkey)
    assert lead.count == 1
    lead = lead.leadRecordList.leadRecord[0]
    attrs = attrs2dict(lead.leadAttributeList)
    print lead.Id, lead.Email
    pprint(attrs)
    if SPECIALCODE and SPECIALVALUE:
        assert attrs[SPECIALCODE] == SPECIALVALUE
    print

    
# As of 1.7, theses are the activity types
# <xs:enumeration value="VisitWebpage"/>
# <xs:enumeration value="FillOutForm"/>
# <xs:enumeration value="ClickLink"/>
# <xs:enumeration value="RegisterForEvent"/>
# <xs:enumeration value="AttendEvent"/>
# <xs:enumeration value="SendEmail"/>
# <xs:enumeration value="EmailDelivered"/>
# <xs:enumeration value="EmailBounced"/>
# <xs:enumeration value="UnsubscribeEmail"/>
# <xs:enumeration value="OpenEmail"/>
# <xs:enumeration value="ClickEmail"/>
# <xs:enumeration value="NewLead"/>
# <xs:enumeration value="ChangeDataValue"/>
# <xs:enumeration value="LeadAssigned"/>
# <xs:enumeration value="NewSFDCOpprtnty"/>
# <xs:enumeration value="Wait"/>
# <xs:enumeration value="RunSubflow"/>
# <xs:enumeration value="RemoveFromFlow"/>
# <xs:enumeration value="PushLeadToSales"/>
# <xs:enumeration value="CreateTask"/>
# <xs:enumeration value="ConvertLead"/>
# <xs:enumeration value="ChangeScore"/>
# <xs:enumeration value="ChangeOwner"/>
# <xs:enumeration value="AddToList"/>
# <xs:enumeration value="RemoveFromList"/>
# <xs:enumeration value="SFDCActivity"/>
# <xs:enumeration value="EmailBouncedSoft"/>
# <xs:enumeration value="PushLeadUpdatesToSales"/>
# <xs:enumeration value="DeleteLeadFromSales"/>
# <xs:enumeration value="SFDCActivityUpdated"/>
# <xs:enumeration value="SFDCMergeLeads"/>
# <xs:enumeration value="MergeLeads"/>
# <xs:enumeration value="ResolveConflicts"/>
# <xs:enumeration value="AssocWithOpprtntyInSales"/>
# <xs:enumeration value="DissocFromOpprtntyInSales"/>
# <xs:enumeration value="UpdateOpprtntyInSales"/>
# <xs:enumeration value="DeleteLead"/>
# <xs:enumeration value="SendAlert"/>
# <xs:enumeration value="SendSalesEmail"/>
# <xs:enumeration value="OpenSalesEmail"/>
# <xs:enumeration value="ClickSalesEmail"/>
# <xs:enumeration value="AddtoSFDCCampaign"/>
# <xs:enumeration value="RemoveFromSFDCCampaign"/>
# <xs:enumeration value="ChangeStatusInSFDCCampaign"/>
# <xs:enumeration value="ReceiveSalesEmail"/>
# <xs:enumeration value="InterestingMoment"/>
# <xs:enumeration value="RequestCampaign"/>
# <xs:enumeration value="SalesEmailBounced"/>
# <xs:enumeration value="ChangeLeadPartition"/>
# <xs:enumeration value="ChangeRevenueStage"/>
# <xs:enumeration value="ChangeRevenueStageManually"/>
# <xs:enumeration value="ComputeDataValue"/>
# <xs:enumeration value="ChangeStatusInProgression"/>
# <xs:enumeration value="ChangeFieldInProgram"/>
# <xs:enumeration value="EnrichWithJigsaw"/>
def test_getLeadActivity():
    print "Testing getLeadActivity"
    leadkey = aLeadKey(email=LEADEMAIL)
    activities = mc.service.getLeadActivity(leadkey,"")
    assert activities.returnCount > 0
    activityrecords = activities.activityRecordList[0]
    assert len(activityrecords) == activities.returnCount
    for activity in activityrecords:
        print "Activity", activity.activityDateTime,activity.activityType
        attrs = attrs2dict(activity.activityAttributes)
        pprint(attrs)
    print
    
def test_requestCampaign():
    print "Testing requestCampaign"
    campaigns = mc.service.getCampaignsForSource("MKTOWS",None,False)
    campaignrecords = campaigns.campaignRecordList[0]
    campaignid = None
    for campaign in campaignrecords:
        if campaign.name == TESTCAMPAIGN:
            print "Found", campaign.id, campaign.name, campaign.description
            campaignid = campaign.id
            break
    assert campaignid != None
    leadkey = aLeadKey(email=LEADEMAIL)
    lead = mc.service.getLead(leadkey)
    assert lead.count == 1
    lead = lead.leadRecordList.leadRecord[0]
    leadid = lead.Id
    # Add key appears to want ID
    leadkey = aLeadKey(id=leadid)
    lka = aLeadKeyArray([leadkey])
    result = mc.service.requestCampaign("MKTOWS", campaignid, lka) 
    assert result.success
    print
    
def test_deleteLeads():
    # Depends on a campaign that deletes leads as they ar added
    # We also need to know the IDNUM for the contacts
    lka = []
    for email in TESTEMAILS:
        leadkey = aLeadKey(email=email)
        lead = mc.service.getLead(leadkey)
        assert lead.count == 1
        lead = lead.leadRecordList.leadRecord[0]
        lka.append(aLeadKey(id=lead.Id))
        print "Found lead", lead.Id, lead.Email
    lka = aLeadKeyArray(lka)
    campaigns = mc.service.getCampaignsForSource("MKTOWS",None,False)
    campaignrecords = campaigns.campaignRecordList[0]
    campaignid = None
    for campaign in campaignrecords:
        if campaign.name == DELETECAMPAIGN:
            print "Found campaign", campaign.id, campaign.name, campaign.description
            campaignid = campaign.id
            break
    assert campaignid != None
    result = mc.service.requestCampaign("MKTOWS", campaignid, lka)
    print result
        
def test_getLeadChanges():
    print "Testing getLeadChanges"
    since = datetime.datetime(year=2010,month=1, day=1)
    changes = mc.service.getLeadChanges("",since,10)
    assert changes.returnCount == 10
    changerecords = changes.leadChangeRecordList[0]
    assert len(changerecords) == changes.returnCount
    for change in changerecords:
        print "leadChange", change.activityDateTime,change.activityType
        pprint(attrs2dict(change.activityAttributes))
    print

def test_getMultipleLeads():
    print "Testing getMultipleLeads"
    lastUpdatedAt = datetime.datetime(year=2010,month=1, day=1)
    leads = mc.service.getMultipleLeads(lastUpdatedAt,None,10)
    assert leads.returnCount == 10
    leadrecords = leads.leadRecordList[0]
    assert len(leadrecords) == 10
    for lead in leadrecords:
        attrs = attrs2dict(lead.leadAttributeList)
        print "Lead", lead.Id, lead.Email
        pprint(attrs)
    print

def test_getMultipleLeadsUnsubscribedFlag():
    print "Testing getMultipleLeadsUnsubscribedFlag"
    lastUpdatedAt = datetime.datetime(year=2010,month=1, day=1)
    attributelist = aStringArray(["Suppressed"])
    leads = mc.service.getMultipleLeads(lastUpdatedAt,None,10, attributelist)
    assert leads.returnCount == 10
    leadrecords = leads.leadRecordList[0]
    assert len(leadrecords) == 10
    for lead in leadrecords:
        attrs = attrs2dict(lead.leadAttributeList)
        print "Lead", lead.Id, lead.Email
        pprint(attrs)
    print

# Valid list operations as of 1.7
# <xs:enumeration value="ADDTOLIST"/>
# <xs:enumeration value="ISMEMBEROFLIST"/>
# <xs:enumeration value="REMOVEFROMLIST"/>

# Valid list types
# <xs:enumeration value="MKTOLISTNAME"/>
# <xs:enumeration value="MKTOSALESUSERID"/>
# <xs:enumeration value="SFDCLEADOWNERID"/>

def test_listOperation():
    print "Testing listOperation"
    # Require numeric id fields
    leadkey = aLeadKey(id=1256) # Is member
    leadkey2 = aLeadKey(id=1) # Is not member
    result = mc.service.listOperation("ISMEMBEROFLIST",aListKey(LEADLIST),
                                      aLeadKeyArray([leadkey,leadkey2]),True)
    print "listOperation", result
                            
def test_syncLead():
    print "Testing syncLead"
    # This test does a create the first time only.
    # The name and email are used in the "standard" marketo API examples
    attrs = dict(FirstName="Sam",LastName="Haggy")
    leadrecord = aLeadRecord(email="shaggy@marketo.com",attributes=dict2attrs(attrs))
    result = mc.service.syncLead(leadrecord, True, None)
    print result.leadId, result.syncStatus.status
    
def test_syncMultipleLeads():
    print "Testing syncMultipleLeads"                      
    leadrecords = []
    for email, (firstname,lastname,domain) in zip(TESTEMAILS, TESTNAMES):
        leadrecord = aLeadRecord(email=email.lower(), attributes=dict2attrs(dict(FirstName=firstname,LastName=lastname)))
        leadrecords.append(leadrecord)
    lra = aLeadRecordArray(leadrecords)
    print lra
    result = mc.service.syncMultipleLeads(lra)
    print result
    print
    
def test_listMObjects():
    print "Testing listMObjects"
    mobjects = mc.service.listMObjects()
    compareData("listMObjects", str(mobjects))
    print
    
def test_describeMObject():
    print "Testing describeMObject"
    mobjects = ["ActivityRecord","LeadRecord","Opportunity","OpportunityPersonRole",]
    descriptions = []
    for mobject in mobjects:
        descriptions.append(str(mc.service.describeMObject(mobject)))
    descriptions = "\n".join(descriptions)
    compareData("describeMObjects", descriptions)
    print


if __name__ == "__main__":
    test_data()
    test_specification()
    test_getLead()
    test_getCampaignsForSource()        
    test_requestCampaign()
    test_getLeadActivity()
    test_getLeadChanges()
    test_listMObjects()
    test_describeMObject()
    test_getLeadActivity()
    test_getMultipleLeads()
    test_getMultipleLeadsUnsubscribedFlag()
    test_listOperation()
    test_syncLead()
    test_syncMultipleLeads()
    test_deleteLeads()
    print "All is well"
