from email.header import Header, decode_header
import poplib
# 解码邮件信息
from email.parser import Parser
import re
import smtplib
from email.mime.text import MIMEText
from email.header import decode_header, Header
import base64


useraccount = 'yourmail@163.com'
password = '验证码'
 
# 邮件服务器地址,以下为网易邮箱
pop3_server = 'pop.163.com'

def sendMail(toMail, myMessage):
    
    mail_host = "smtp.163.com"
    mail_user = "yourmail@163.com"
    mail_pass = "授权码"
    receivers = toMail
    message = MIMEText(myMessage, 'plain', 'utf-8')
    subject = u'SUDA Charging Piles Monitor'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(mail_user,  receivers, message.as_string())
        print (f"{receivers} 邮件发送成功")
    except smtplib.SMTPException:
        print ("Error: 无法发送邮件")



def CXreply(toMail,dict,groupname,tipsDict):
    #translateDict={'东吴桥下':'Under DongWu Bridge','东七宿舍楼':'East 7 Dormitory','本七宿舍楼':'Center 7 Dormitory','逸夫楼':'YiFu Building','文思楼':'WenSi Building','一号机':'Machine.NO.1','二号机':'Machine.NO.2','三号机':'Machine.NO.3','一号机 (不支持扫码支付)':'(NO.1 Pile Do NOT support scan to pay)'}
    translateDict={'东吴桥下':'Under DongWu Bridge','东七宿舍楼':'East 7 Dormitory','本七宿舍楼':'Center 7 Dormitory','逸夫楼':'YiFu Building',\
    '文思楼':'WenSi Building','一号机':'Machine.NO.1','二号机':'Machine.NO.2','三号机':'Machine.NO.3',\
        '食堂':'Canteen','1C号楼':'NO.1C Building','1B号楼':'NO.1B Building','B02号楼':'NO.B02 Building','B04号楼':'NO.B04 Building',\
            '201号楼':'NO.201 Building','109号楼':'NO.109 building','食堂西北角':'Northwest corner of Canteen','104号楼':'NO.104 building',\
                '01180111':'Machine.01180111','01180146':'Machine.01180146','01180112':'Machine.01180112','01180193':'Machine.01180193','01180074':'Machine.01180074','01180110':'Machine.01180110',\
                    '01180192':'Machine.01180192','01180050':'Machine.01180050','01180058':'Machine.01180058'}
    message=translateDict[groupname]+' Charging piles standing by:\n===========\n'
    for key,value in dict.items():
        message+= '\t***'+translateDict[key]+':***\n'
        standbyList = [it for it in value if value[it]=='standby']
        message+= '\t\t'+', '.join(standbyList)+'\n=========================================\n'

    if groupname=='东吴桥下':
        message+='\n******'+translateDict[groupname]+' (Machine.NO.1 Do NOT support scan to pay)******'
    sendMail(toMail,message)
    #print(dict)
    return







# 下面的用不到了

def sendMail_old(toMail,myMessage):
    # 25端口被阿里云ban了
    #设置服务器所需信息
    #163邮箱服务器地址
    mail_host = 'smtp.163.com'  
    #163用户名
    mail_user = 'yourmail'  
    #密码(部分邮箱为授权码) 
    mail_pass = '授权码'   
    #邮件发送方邮箱地址
    sender = 'yourmail@163.com'  
    #邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    #receivers = ['496373158@qq.com']  
    #设置email信息
    #邮件内容设置
    message = MIMEText(myMessage,'plain','utf-8-sig')
    #邮件主题       
    message['Subject'] = 'SUDA Charging Piles Monitor'
    #发送方信息
    message['From'] = useraccount
    #接受方信息     
    #message['To'] = ','.join(toMail)  

    #登录并发送邮件
    try:
        smtpObj = smtplib.SMTP() 
        #连接到服务器
        smtpObj.connect(mail_host,25)
        #登录到服务器
        smtpObj.login(mail_user,mail_pass) 
        #发送
        smtpObj.sendmail(
            sender,toMail,message.as_string()) 
        #退出
        smtpObj.quit() 
        print(toMail + ' success')
    except smtplib.SMTPException as e:
        print('error',e) #打印错误

def JKreply(toMail):
    message='已开始监控!'
    sendMail(toMail,message)
    return

def sendOhNo(toMail,target):
    message='-'.join(target)+'已停止充电！'
    sendMail(toMail,message)
    return



def get_new_email():
    # 开始连接到服务器
	server = poplib.POP3(pop3_server)
	# 打开或者关闭调试信息，为打开，会在控制台打印客户端与服务器的交互信息
	server.set_debuglevel(0)

	# 开始进行身份验证
	server.user(useraccount)
	server.pass_(password)


	rsp, msg_list, rsp_siz = server.list()

	# 下面单纯获取最新的一封邮件
	total_mail_numbers = len(msg_list)
	rsp, msglines, msgsiz = server.retr(total_mail_numbers)
	msg_content = b'\r\n'.join(msglines).decode('utf-8-sig')
	msg = Parser().parsestr(text=msg_content)
 
	# 关闭与服务器的连接，释放资源
	server.close()
 
	return msg

def getSubject(msg):
    subject = msg['Subject']
    value, charset = decode_header(subject)[0]
    if charset:
        value = value.decode(charset)
    return value

# 正文信息是被base64编码后的串，需要获取编码格式进行解码
def parser_content(msg):
    content = msg.get_payload()

    # 文本信息
    content_charset = msg.get_content_charset()  # 获取编码格式
    try:
        text_content = base64.b64decode(content).decode(content_charset)  # base64解码
    # print(type(content))
    except:
        text_content = ''

    return text_content

def getEmailContent():
    msg = get_new_email()
    res = re.search(re.compile('<(.*?)>',re.S),msg['from'])
    userEmail=res.group(1)
    # res = re.search(re.compile('Subject: (.*?)\s*X',re.S),msg)

    userCommand=[getSubject(msg),msg['date']]
    temp = parser_content(msg)
    if temp == '':
        sendMail(userEmail,'请使用苹果自带邮件app发送！')
    res = re.search(re.compile('(\S*)',re.S),temp)
    userTargetText=res.group(1).strip('\ufeff')

    #print(msg)

    return userEmail,userCommand,userTargetText


    # print(userEmail)
    # print(userCommand)
    # print(userTargetText)
