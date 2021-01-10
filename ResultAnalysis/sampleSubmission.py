import requests
import random
from datetime import datetime


def DATABASE_URL(sub):
    url = 'http://192.168.1.200:8001'
    return f"{url}{sub}"


def getNonReportedSampleFromServer():
    "fetch all non reporeted samples"
    return requests.get(DATABASE_URL('/samples/?page=0&perpage=9999'),json={
        'reporeted':False
    })

def samplesToFirestore(samples):
    "parse samples doc from my server to upload to firebase"
    cols=['result','N7','RP4','N7_NTC','N7_NTC_CV','N7_PTC','N7_PTC_CV','N7_NBC_CV',
                'RP4_NTC','RP4_NTC_CV','RP4_PTC','RP4_PTC_CV','RP4_NBC_CV','testStart','testEnd']
    results =[]
    for s in samples:
        docID = s['extId']
        details = {
            'type':s['type'],
            'comment':'No comment.',
            'collectAt': s['created'],
            'plateId': s['sPlate'], # this plate id is storage plate ID
            'sampleId': s['sampleId']
        }        
        for i in cols:
            details[i] = s['results'][-1].get(i,'')

        results.append({'docID':docID,'details':details})
    return results


def URL(sub):
    url = 'http://localhost:5000/ams-clia/us-central1/api'
    return f'{url}{sub}'

def login(username,pwd):
    res = requests.post(URL('/user/login'),json={'email':username,'password':pwd})
    if res.status_code == 200:
        return res.json()['token']
    else:
        return res
        
def uploadResult(result,token):
    headers = {'Authorization':f'Bearer {token}'}
    res = requests.post(URL('/result/upload'),json=result,headers=headers)
    if res.status_code==200:
        return res.json()
    else:
        return res

def getAprrove(token):
    headers = {'Authorization':f'Bearer {token}'}
    res = requests.get(URL('/result/toApprove'),headers=headers)
    if res.status_code==200:
        return res.json()
    else:
        return res

def randRange(a,b,fix=2):
    return round( random.random()*(b-a)+a,fix)


def randResult():
    new =  {
    'N7': randRange(1,7),
    'RP4': randRange(4,10),
    'N7_PTC':randRange(1.8,3),
    'RP4_PTC':randRange(1.8,3),
    'N7_NTC':randRange(1,3),
    'RP4_NTC':randRange(1,4),
    'NBC_CV':randRange(0,0.05,fix=4),
    'type':'saliva',
    "sampleId":str(int(round(random.random()*1e10))),
    "plateId":str(int(round(random.random()*1e10))),
    'collectAt':datetime.now().isoformat(),
    'testStart':datetime.now().isoformat(),
    'testEnd':datetime.now().isoformat(),
    'comment':'None'    
    }
    new['result'] = callResult(new)
    return new

def callResult(res):
    if res['NBC_CV'] > 0.05:return 'Invalid:CV'
    if res['N7_NTC'] >= 5: return 'Invalid:N7NTC'
    if res['RP4_NTC'] >= 5: return 'Invalid:RP4NTC'
    if res['N7_PTC'] <=1.8: return 'Invalid:N7PTC'
    if res['RP4_PTC'] <=1.8: return 'Invalid:RP4PTC'
    if res['N7']>5:return 'Positive'
    if res['RP4']<5:return 'Invalid:RP4'
    return 'Negative'

def generateResult(N):
    result = []
    for i in range(N):
        res = randResult()
        result.append({
        'docID': '/booking/tN2fdLwz0tpfQKfGeAHl',        
        'details':res,        
        })
    return result

def deleteApproved(token):
    res = requests.delete(URL('/result/approved'),
        headers = {'Authorization':f'Bearer {token}'})
    return res.json()


token = login('admin@ams.com','password')

res = getNonReportedSampleFromServer()
samples = res.json()

results = samplesToFirestore(samples)



res = uploadResult(results,token)

res = getAprrove(token)

res = deleteApproved(token)





