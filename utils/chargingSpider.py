from random import choice
import requests

def getTextFromURL(targetURL):
    '''
    use spider to get text from target url
    '''
    user_agent_list=['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko)','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0','Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)','Opera/9.80 (Windows NT 6.1; WOW64; U; zh-cn) Presto/2.10.229 Version/11.62']


    try:
        kv = {'user-agent': choice(user_agent_list)}
        r = requests.get(targetURL, headers=kv)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        # res=re.search(pattern0,r.text)
        #     print('无货')
        return r.text
    except:
        # print("爬取失败")
        return 'failed.'
