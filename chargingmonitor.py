from time import sleep
from chargingSpider import getTextFromURL
from textProcess import Text2Dict
from mailTools import CXreply, sendMail
import pickle

READJKFILE_TIME = 5 # 监控 READJKFILE_TIME秒一次
SPIDER_TIME = 15    # 爬虫 SPIDER_TIME秒一次
MAX_TIME = 1440 # 最长监控时间
FAILDED_COUNT = 5

user_agent_list=['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko)','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0','Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)','Opera/9.80 (Windows NT 6.1; WOW64; U; zh-cn) Presto/2.10.229 Version/11.62']
# chargingURL='http://10.20.7.127:5000/'
chargingURL='http://sudacharge.haoxiaoren.com'
dshURL='http://sudacharge.haoxiaoren.com/?region=DSH'
ychURL='http://sudacharge.haoxiaoren.com/?region=YCH'
groupList=['东吴桥下','东七宿舍楼','本七宿舍楼','逸夫楼','文思楼']
groupList_dsh=['B02号楼','B04号楼','201号楼','109号楼','食堂西北角','104号楼']
groupList_ych=['食堂','1C号楼','1B号楼']

translateDict={'东吴桥下':'Under DongWu Bridge','东七宿舍楼':'East 7 Dormitory','本七宿舍楼':'Center 7 Dormitory','逸夫楼':'YiFu Building',\
    '文思楼':'WenSi Building','一号机':'Machine.NO.1','二号机':'Machine.NO.2','三号机':'Machine.NO.3',\
        '食堂':'Canteen','1C号楼':'NO.1C Building','1B号楼':'NO.1B Building','B02号楼':'NO.B02 Building','B04号楼':'NO.B04 Building',\
            '201号楼':'NO.201 Building','109号楼':'NO.109 building','食堂西北角':'Northwest corner of Canteen','104号楼':'NO.104 building',\
                '01180111':'Machine.01180111','01180146':'Machine.01180146','01180112':'Machine.01180112','01180193':'Machine.01180193','01180074':'Machine.01180074','01180110':'Machine.01180110',\
                    '01180192':'Machine.01180192','01180050':'Machine.01180050','01180058':'Machine.01180058'}


def writepickle(filename,data):
    with open(filename, 'wb') as f:
        f.write(pickle.dumps(data))

def readpickle(filename):
    one_pickle_data=[]
    with open(filename, 'rb') as f:
        try:
            one_pickle_data = pickle.loads(f.read())
        except:
            pass
    return one_pickle_data


def Monitor1Epoch(userEmailList,userTargetList,userStatusList,failedCount):

    # 爬一次
    urlText = getTextFromURL(chargingURL)
    urlText_dsh = getTextFromURL(dshURL)
    urlText_ych = getTextFromURL(ychURL)
    # 爬取失败failedCount - 1
    if urlText == 'failed.':
        failedCount -= 1
        return 0,0,0,failedCount,0,0,0
    # 爬取成功failedCount重置
    failedCount = FAILDED_COUNT

    chargingDict,groupItemDict,tipsDict = Text2Dict(urlText, groupList)
    chargingDict_dsh,groupItemDict_dsh,tipsDict_dsh = Text2Dict(urlText_dsh, groupList_dsh)
    chargingDict_ych,groupItemDict_ych,tipsDict_ych = Text2Dict(urlText_ych, groupList_ych)
    # tipsDict = tipsDict.update(tipsDict_dsh)
    # tipsDict = tipsDict.update(tipsDict_ych)
    chargingDictMain = {'天赐庄':chargingDict,'独墅湖':chargingDict_dsh,'阳澄湖':chargingDict_ych}


    newEmailList=[]
    newTargetList=[]
    newStatusList=[]
    for index,item in enumerate(userTargetList):
        # print(chargingDict)
        if chargingDictMain[item[0]][item[1]][item[2]][item[3]] != 'charging':
            # 充电停止
            sendMail(userEmailList[index], '{}, {}, {} has stopped charging!'.format(translateDict[item[1]],translateDict[item[2]],item[3]))
        
        elif userStatusList[index] - 1 == 0:
            # 计时归零
            sendMail(userEmailList[index], '{}, {}, {} has been charged for 6 hours, stopping monitoring.'.format(translateDict[item[1]],translateDict[item[2]],item[3]))
        else:
            # 其他计时-1
            newEmailList.append(userEmailList[index])
            newTargetList.append(userTargetList[index])
            newStatusList.append(userStatusList[index]-1)
    return chargingDictMain,groupItemDict,tipsDict,failedCount,\
        newEmailList,newTargetList,newStatusList

if __name__ == '__main__':


    readJKFileCount = READJKFILE_TIME
    spiderCount = SPIDER_TIME
    failedCount = FAILDED_COUNT

    userEmailList=[]
    userTargetList=[]
    userStatusList=[]
    chargingDict={}
    groupItemDict={}
    tipsDict={}
    chargingDictMain={}

    JK = 'JK.pkl'
    CX = 'CX.pkl'
    while 1:
        # 爬虫 SPIDER_TIME秒一次
        if failedCount==0:
            # 连续爬取失败FAILED_COUNT次，服务器可能在维修
            spiderCount = 300
        if spiderCount == SPIDER_TIME:
            chargingDictMain0,groupItemDict0,tipsDict0,failedCount,\
                newEmailList,newTargetList,newStatusList=\
                    Monitor1Epoch(userEmailList,userTargetList,userStatusList,failedCount)
            if failedCount==5:
                # 爬取成功，覆盖List
                userEmailList = newEmailList
                userTargetList = newTargetList
                userStatusList = newStatusList
                chargingDictMain,groupItemDict,tipsDict = chargingDictMain0,groupItemDict0,tipsDict0
            pass
        elif spiderCount==0:
            spiderCount = SPIDER_TIME+1
            
        CXlist = readpickle(CX)
        for [itemEmail,itemXQ,itemGroup] in CXlist:
            CXreply(itemEmail,chargingDictMain[itemXQ][itemGroup],itemGroup,tipsDict)
        clearList=[]
        writepickle(CX,clearList)
    
        if readJKFileCount==READJKFILE_TIME:
            JKlist=readpickle(JK)
            for [itemEmail,itemTarget] in JKlist:
                if itemTarget[3] not in chargingDictMain[itemTarget[0]][itemTarget[1]][itemTarget[2]]:
                    sendMail(itemEmail,'{}, {}, {} is offline or not existed! please change pile.'.format(translateDict[itemTarget[1]],translateDict[itemTarget[2]],itemTarget[3]))
                elif chargingDictMain[itemTarget[0]][itemTarget[1]][itemTarget[2]][itemTarget[3]] == 'offline':
                    sendMail(itemEmail,'{}, {}, {} is offline! please change pile.'.format(translateDict[itemTarget[1]],translateDict[itemTarget[2]],itemTarget[3]))
                elif (itemEmail in userEmailList) and (userTargetList[userEmailList.index(itemEmail)] != itemTarget):
                    userTargetList[userEmailList.index(itemEmail)] = itemTarget
                    userStatusList[userEmailList.index(itemEmail)] = MAX_TIME
                    sendMail(itemEmail,'You have changed your monitor target to: {}, {}, {}.'.format(translateDict[itemTarget[1]],translateDict[itemTarget[2]],itemTarget[3]))
                elif itemEmail not in userEmailList:
                    userEmailList.append(itemEmail)
                    userTargetList.append(itemTarget)
                    userStatusList.append(MAX_TIME)
                    sendMail(itemEmail,'Start Monitoring with target: {}, {}, {}.'.format(translateDict[itemTarget[1]],translateDict[itemTarget[2]],itemTarget[3]))
                else:
                    sendMail(itemEmail,'Do not submit again! You have been monitoring target:{}, {}, {}.'.format(translateDict[itemTarget[1]],translateDict[itemTarget[2]],itemTarget[3]))

            clearList=[]
            writepickle(JK,clearList)
        elif readJKFileCount==0:
            readJKFileCount = READJKFILE_TIME+1
        
        readJKFileCount-=1
        spiderCount-=1

        sleep(1)
