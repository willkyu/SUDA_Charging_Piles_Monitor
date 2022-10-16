import re



def Block2dict(blockText):
    iNumList=re.findall(re.compile('<div class="col">\s*<div.*?>\s*(.*?)\s*</div>',re.S),blockText)
    iStatusList=re.findall(re.compile('(standby|offline|charging)',re.S), blockText)
    blockDict=dict(zip(iNumList,iStatusList))
    return blockDict

def getBlock(groupText):
    numPattern = re.compile('posonline">\s*(.*?)\s*</div>',re.S)
    groupDic = {}
    numList = re.findall(numPattern,groupText)
    tips=[]
    #print(numList)
    for num in numList:
        num0=num
        if '(' in num:
            num0=re.sub('\(.*?\)','',num)
            num0 = num0.strip()
            tips.append(num)
        blockPattern = re.compile(num0+'(.*?)</div>\s*</div>\s*</div>',re.S)
        res=re.search(blockPattern,groupText)
        #print(groupText)
        blockText = res.group(1)
        blockDict = Block2dict(blockText)
        groupDic[num0]=blockDict
    return groupDic, numList, tips



def Text2Dict(urlText, groupList):
    '''
    extract charging dict from url got
    '''
    chargingDict={}
    groupItemDict={}
    tipsDict={}

    for group in groupList:
        pattern = re.compile(group+'(.*?)(<div class="accordion-item">|</body>)', re.S)
        res = re.search(pattern,urlText)
        groupText=res.group(1)
        
        groupDic,groupItemList, tips= getBlock(groupText)
        tipsDict[group]=tips
        chargingDict[group]=groupDic
        groupItemDict[group]=groupItemList
        
    return chargingDict,groupItemDict,tipsDict