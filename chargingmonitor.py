from time import sleep
from utils.chargingSpider import getTextFromURL
from utils.textProcess import Text2Dict
from utils.mailTools import CXreply, sendMail
import pickle

READJKFILE_TIME = 5 # 监控 READJKFILE_TIME秒一次
SPIDER_TIME = 15    # 爬虫 SPIDER_TIME秒一次
MAX_TIME = 1440 # 最长监控时间
FAILDED_COUNT = 5

user_agent_list=['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko)','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0','Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)','Opera/9.80 (Windows NT 6.1; WOW64; U; zh-cn) Presto/2.10.229 Version/11.62']
# chargingURL='http://10.20.7.127:5000/'
chargingURL='http://sudacharge.haoxiaoren.com'
groupList=['东吴桥下','东七宿舍楼','本七宿舍楼','逸夫楼','文思楼']
translateDict={'东吴桥下':'Under DongWu Bridge','东七宿舍楼':'East 7 Dormitory','本七宿舍楼':'Center 7 Dormitory','逸夫楼':'YiFu Building','文思楼':'WenSi Building','一号机':'Machine.NO.1','二号机':'Machine.NO.2','三号机':'Machine.NO.3'}


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
    # 爬取失败failedCount - 1
    if urlText == 'failed.':
        failedCount -= 1
        return 0,0,0,failedCount,0,0,0
    # 爬取成功failedCount重置
    failedCount = FAILDED_COUNT

    chargingDict,groupItemDict,tipsDict = Text2Dict(urlText, groupList)

    newEmailList=[]
    newTargetList=[]
    newStatusList=[]
    for index,item in enumerate(userTargetList):
        # print(chargingDict)
        if chargingDict[item[0]][item[1]][item[2]] != 'charging':
            # 充电停止
            sendMail(userEmailList[index], '{}, {}, {} has stopped charging!'.format(translateDict[item[0]],translateDict[item[1]],item[2]))
        
        elif userStatusList[index] - 1 == 0:
            # 计时归零
            sendMail(userEmailList[index], '{}, {}, {} has been charged for 6 hours, stopping monitoring.'.format(translateDict[item[0]],translateDict[item[1]],item[2]))
        else:
            # 其他计时-1
            newEmailList.append(userEmailList[index])
            newTargetList.append(userTargetList[index])
            newStatusList.append(userStatusList[index]-1)
    return chargingDict,groupItemDict,tipsDict,failedCount,\
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
    chargingDict={}

    JK = '/anaconda/pythoncode/ChargingMonitor/JK.pkl'
    CX = '/anaconda/pythoncode/ChargingMonitor/CX.pkl'
    while 1:
        # 爬虫 SPIDER_TIME秒一次
        if failedCount==0:
            # 连续爬取失败FAILED_COUNT次，服务器可能在维修
            spiderCount = 300
        if spiderCount == SPIDER_TIME:
            chargingDict0,groupItemDict0,tipsDict0,failedCount,\
                newEmailList,newTargetList,newStatusList=\
                    Monitor1Epoch(userEmailList,userTargetList,userStatusList,failedCount)
            if failedCount==5:
                # 爬取成功，覆盖List
                userEmailList = newEmailList
                userTargetList = newTargetList
                userStatusList = newStatusList
                chargingDict,groupItemDict,tipsDict = chargingDict0,groupItemDict0,tipsDict0
            pass
        elif spiderCount==0:
            spiderCount = SPIDER_TIME+1
            
        CXlist = readpickle(CX)
        for [itemEmail,itemGroup] in CXlist:
            CXreply(itemEmail,chargingDict[itemGroup],itemGroup,tipsDict)
        clearList=[]
        writepickle(CX,clearList)
    
        if readJKFileCount==READJKFILE_TIME:
            JKlist=readpickle(JK)
            for [itemEmail,itemTarget] in JKlist:
                if chargingDict[itemTarget[0]][itemTarget[1]][itemTarget[2]] == 'offline':
                    sendMail(itemEmail,'{}, {}, {} is offline! please change pile.'.format(translateDict[itemTarget[0]],translateDict[itemTarget[1]],itemTarget[2]))
                elif (itemEmail in userEmailList) and (userTargetList[userEmailList.index(itemEmail)] != itemTarget):
                    userTargetList[userEmailList.index(itemEmail)] = itemTarget
                    userStatusList[userEmailList.index(itemEmail)] = MAX_TIME
                    sendMail(itemEmail,'You have changed your monitor target to: {}, {}, {}.'.format(translateDict[itemTarget[0]],translateDict[itemTarget[1]],itemTarget[2]))
                elif itemEmail not in userEmailList:
                    userEmailList.append(itemEmail)
                    userTargetList.append(itemTarget)
                    userStatusList.append(MAX_TIME)
                    sendMail(itemEmail,'Start Monitoring with target: {}, {}, {}.'.format(translateDict[itemTarget[0]],translateDict[itemTarget[1]],itemTarget[2]))
                else:
                    sendMail(itemEmail,'Do not submit again! You have been monitoring target:{}, {}, {}.'.format(translateDict[itemTarget[0]],translateDict[itemTarget[1]],itemTarget[2]))

            clearList=[]
            writepickle(JK,clearList)
        elif readJKFileCount==0:
            readJKFileCount = READJKFILE_TIME+1
        
        readJKFileCount-=1
        spiderCount-=1

        sleep(1)
