import db

def setDomains(domainsList, subName):
    db.connect(subName)
    activeOnDomainsList = getRelevantDomains(subName)

    payload = []

    for item in domainsList:
        if item in activeOnDomainsList:
            continue
        else:
            payload.append(item)

    db.setDomains(payload)

def unsetDomains(domainsList, subName):
    db.connect(subName)
    activeOnDomainsList = getRelevantDomains(subName)

    payload = []

    for item in domainsList:
        if item in activeOnDomainsList:
            payload.append(item)
        else:
            continue

    db.unsetDomains(payload)

def isActiveOnDomain(domainName, subName):
    activeOnDomainsList = getRelevantDomains(subName)

    if domainName in activeOnDomainsList:
        return True
    else:
        return False


def blacklistDomain(domainsList, subName):
    db.connect(subName)
    db.blacklistDomain(domainsList)

def getRelevantDomains(subName):
    db.connect(subName)
    return db.getRelevantDomains()

def getBlacklistedDomains(subName):
    db.connect(subName)
    return db.getBlacklistedDomains
