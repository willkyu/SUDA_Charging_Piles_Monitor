from flask import Flask, request
from flask_cors import *
import pickle
import threading
q=threading.Lock()
app = Flask(__name__)
CORS(app, resources=r'/*')

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

@cross_origin(supports_credentials=True)
@app.route("/t", methods=["POST"])
def index():
    try:
        userEmail_param,userCommand_param='',''
        print(request.get_json())
        if request.method == "POST":
            data = request.get_json()
            print(data) 
            if 'lmy'==data['key'][8:11]:
                userEmail_param=data['useremail']
                userCommand_param='监控' if data['type']==2 else '查询'
                if userCommand_param=='查询':
                    region1=data['region1']
                    # q.acquire()
                    pickledata=readpickle('/anaconda/pythoncode/ChargingMonitor/CX.pkl')
                    pickledata.append([userEmail_param,region1])
                    writepickle('/anaconda/pythoncode/ChargingMonitor/CX.pkl',pickledata)
                    # q.release()
                elif userCommand_param=='监控':
                    region1,region2,region3=data['region1'],data['region2'],'0'+str(data['region3']) if len(str(data['region3']))==1 else str(data['region3']) 
                    # q.acquire()
                    pickledata=readpickle('/anaconda/pythoncode/ChargingMonitor/JK.pkl')
                    pickledata.append([userEmail_param,[region1,region2,region3]])
                    writepickle('/anaconda/pythoncode/ChargingMonitor/JK.pkl',pickledata)
                    # q.release()
                else:
                    return {'state':'error1'}
                print(f'{userEmail_param} {userCommand_param} 成功')
                return {'state':'sucess'}
            else:
                return {'state':'error2'}
    except Exception as ex:
        print(ex)
        return {'state':'error3'}
@cross_origin(supports_credentials=True)
@app.route("/a", methods=["GET"])
def test():
    return '6666'
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8888)

    