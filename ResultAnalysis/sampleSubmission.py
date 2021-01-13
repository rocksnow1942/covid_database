import requests
import random
from datetime import datetime


def DATABASE_URL(sub):
    url = 'http://192.168.1.200:8001'
    return f"{url}{sub}"


def getNonReportedSampleFromServer():
    "fetch all non reporeted samples"
    return requests.get(DATABASE_URL('/samples/?page=0&perpage=9999'),json={
        'reported':False
    }).json()

def filterSamplesWithResults(s):
    #return only samples that have reuslts.
    res = []
    for i in s:
        if i.get('results') and i.get('results')[-1].get('testEnd',False):
            res.append(i)
    return res

def setSamplesToReported(samples):
    " marke samples as reporeted in server."
    return requests.put(DATABASE_URL('/samples'),json=[{'sampleId':s['sampleId'],'reported':True} for s in samples])


def samplesToFirestore(samples):
    "parse samples doc from my server to upload to firebase, right now only submit the last result."
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
    "for firebase"
    # url = 'http://localhost:5000/ams-clia/us-central1/api'
    url = 'https://us-central1-ams-clia.cloudfunctions.net/api'
    return f'{url}{sub}'

def login(username,pwd):
    'get the token from firebase'
    res = requests.post(URL('/user/login'),json={'email':username,'password':pwd})
    if res.status_code == 200:
        return res.json()['token']
    else:
        return res
        
def uploadResult(result,token):
    "upload result to firebase."
    headers = {'Authorization':f'Bearer {token}'}
    res = requests.post(URL('/result/upload'),json=result,headers=headers)
    if res.status_code==200:
        return res.json()
    else:
        return res

def getAprrove(token):
    "get need to approve results."
    headers = {'Authorization':f'Bearer {token}'}
    res = requests.get(URL('/result/toApprove'),headers=headers)
    if res.status_code==200:
        return res.json()
    else:
        return res

def randRange(a,b,fix=2):
    return round( random.random()*(b-a)+a,fix)

def deleteApproved(token):
    res = requests.delete(URL('/result/approved'),
        headers = {'Authorization':f'Bearer {token}'})
    return res.json()


token = login('admin@ams.com','password') 

samples = getNonReportedSampleFromServer()

samples

len(samples)

res = setSamplesToReported(samples)

res.json()

withResultSamples = filterSamplesWithResults(samples)

results = samplesToFirestore(withResultSamples)



res = uploadResult(results,token)

res = getAprrove(token)

res = deleteApproved(token)





