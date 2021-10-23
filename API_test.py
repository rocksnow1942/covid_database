import requests
import random 
from bson.objectid import ObjectId
import time
from datetime import datetime
import dateutil.parser
from dateutil import tz

def parseISOTime(ts):
    "turn mongo time stamp to python datetime object."
    dt = dateutil.parser.parse(ts)
    return dt.astimezone(tz.tzlocal())


def IDgen():
    "generate random 10 digit ID"
    return f"{int(random.random()*1e10):010d}"

def randWell():
    "generate random well label"
    return random.choice('ABCDEFGH')+f'{random.randint(1,12)}'

def createSamples(N):
    samples = []
    for i in range(N):
        samples.append({
        'sampleId':IDgen(),
        'patientId':str(ObjectId()),
        'sPlate':IDgen(),
        'sWell':randWell()
        })
    return samples


def createPlate():
    wells = {}
    for c in range(1,13):
        for r in 'ABCDEFGH':
            wells[f'{r}{c}'] = {
                'sampleId':IDgen(),
                'type':'ukn-N7',
            }            
    return {
        'plateId':IDgen(),
        'step':random.choice(['lyse','lamp']),
        'layout':random.choice(['96Sample','96Ctrl','48Sample']),
        'wells':wells,
        }

def createWellsRaw():
    wells = {}
    for c in range(1,13):
        for r in 'ABCDEFGH':
            wells[f'{r}{c}'] = {
                'raw':int(random.random()*1e4)
            }
    return wells
    
def createPatients(N=10):
    ps = []
    for i in range(N):
        ps.append(dict(
        name='patient - '+str(i+1),
        dob=f'1988-10-{i+2:02}',
        email='testemail@gmail.com',
        tel='999-888-1234',
        age=random.randint(30,50),
        gender=random.choice(['male','female','other']),
        address = 'asdf@joasd',
        company = 'a test company',
        extId = IDgen(),
        sampleIds=[]
        ))
    return ps

# Test Sample Route
URL = 'http://192.168.1.200:8001/samples'

URL = 'http://localhost:8001'

res = requests.get('https://github.com/rocksnow1942/covid_database/blob/master/package.json')

res.text.index('version')
 

import json

json.loads(res.text)['version']

res = requests.get(URL+'/?page=0&perpage=1',json={'sampleId':'4044939412'})
len(res.json())
res.status_code
sample = res.json()
sample
res = requests.post(URL+'/addOneSample',json=sample[0])

res.status_code

res.json()



newSample = res.json()[0]
newSample['sampleId'] = 'TEST'
newSample.pop('extId')
res = requests.post(URL+'/addOneSample',json=newSample)

res.json()

newResults = [{'sampleId':'4044939352','results': [
{'plateId': ['3140000158', '4090000162'],
    'N7_NTC': 0.63,
    'N7_PTC': 1.81,
    'N7_NTC_CV': 1.31,
    'N7_PTC_CV': 2.53,
    'N7_NBC_CV': 0.94,
    'RP4_NTC': 1.55,
    'RP4_PTC': 2.38,
    'RP4_NTC_CV': 2.2,
    'RP4_PTC_CV': 2.33,
    'RP4_NBC_CV': 1.76,
    'testStart': '2021-01-11T21:36:33.711Z',
    'comment': '',
    'N7': 0.05,
    'RP4': 8.15,
    'result': 'Negative',},
] }]


newResults

res = requests.post(URL+'/results',json=newResults)
res.json()


res = requests.post(URL,json=[{     
    "type": "saliva",     
    "sampleId": "12345",
    "extId": "/booking/Nswmu1",
    "created":"2020/01/10 10:12",
    "meta": {
        "name": "Hui Bang"
    },
}])
parseISOTime('2020-01-10T18:12:00.000Z')
res.json()


samples = createSamples(10)

# get samples
res = requests.get(URL+'/?page=0&perpage=10000000',)
len(res.json())
res.json()
ids = [IDgen() for i in range(100000)]
len(ids)
# query samples
res = requests.get(URL,json={"sampleId":{'$in':['0690824456','3183992925',""]}})
res.status_code==200
len(res.json())
res.json()

# get One sample by Id
res = requests.get(URL+'/samples/id/123',)
res
len(res.json())
res.json()


# insert new samples


t0 = time.perf_counter()
for i in range(10):
    samples = createSamples(960)
    res = requests.post(URL,json = samples)
t1 = time.perf_counter()-t0
print(t1)
len(res.json())
res.json()[0]
res.status_code
updateSample = samples[0:3]
old = samples[0:2]
res = requests.post(URL,json = old +samples )
res.status_code
res.json()
updateSample

for s in samples[0:3]:
    s['results'] = [{
            "diagnose": random.choice(['positive','negative']),
            "testOn":[IDgen()],
            "desc": "a description",
            "an extra":'extra 1',
            'note': 'a note'
    },{
            "diagnose": random.choice(['positive','negative']),
            "testOn":[IDgen()],
            "desc": "a description",
            "an extra":'extra 2'
    }]

# update samples
samples[4:6]
putres = requests.put(URL,json=samples[4:6]+[{'sampleId': '0690824456',
  'patientId': '5fd5923c76a35ab2f4bd96e5',
  'sPlate': '9271107760',
  'sWell': 'C7'}])
len(putres.json())
putres.json()

# upsert takes longer, but scales OK for now.
samples = createSamples(96)
newsample = createSamples(2)
oldsample = samples[0:2]
oldsample
oldsample[1].update(sPlate='1234567890',sWell='F1')




print('\n'.join(i['sampleId'] for i in samples))
t0 = time.perf_counter()
upres = requests.post(URL+'/samples/upsert',json=samples)
t1 = time.perf_counter()-t0
print(t1)
upres.status_code
len(upres.json())
print(upres.json())

c = upres.json()['created']
'3245901920' in c

ids = upres.json()['updated']

allsamples = requests.get(URL+'/samples',json={'sampleId':{"$in":['3509147856', '7423913175','8650534795', '5394416872']}})
len(allsamples.json())
newsample
allsamples.json()

# get one sample with sampleId
requests.get(URL+f'/samples/id/{samples[0]["sampleId"]}').json()

# delete samples:
samples = res.json()
res = requests.delete(URL,json=[{'sampleId':'12345'}])
res.status_code
res.json()

# append results
res = requests.post(URL+'/results',json=samples[0:3])
res.json()



# test Plate route
PlateURL = 'http://localhost:8001/plates'

# get new plate
res = requests.get(PlateURL+'/?page=0&perpage=10',json={'plateId':'6125506475'})
res.status_code
len(res.json())
res.json()
# get one plate
res = requests.get(PlateURL+'/id/612550647',)

res.status_code

res.json()

# post new plate
plate = createPlate()
plate2 = createPlate()
plate['layout']='test'
res = requests.post(PlateURL,json=plate)
res = requests.post(PlateURL,json=plate2)
res.status_code
res.json()

PlateURL
# link plate
oldId = plate2['plateId']
res = requests.put(PlateURL+'/link',json={'oldId':"234",'newId':"123",'step':'lyse','companion':'456'})

res.status_code
res.json()

# update raw data
update = {
'plateId':plate2['plateId'],
'wells':createWellsRaw()
}

res = requests.put(PlateURL,json=update)
res.status_code
res.json()
parseISOTime(res.json()['created'])



# delete one plate
res = requests.delete(PlateURL,json=plate2)
res.status_code
res.json()





# storage Route
StoreURL  = 'http://localhost:8001/store'


res = requests.get(StoreURL+'/empty')
res.status_code
res.json()

# create position
positions = [{'location':randWell()} for i in range(2)]

positions = [{'location': 'A3'}, {'location': 'A4'}] 
res = requests.post(StoreURL+'/location',json=positions)
res.status_code
res.json()


# delete positions
positions = [{'location':randWell()} for i in range(1000)]
res = requests.delete(StoreURL + '/location',json=[{'location':'D11'},{'location':'A2'}])
res.status_code
res.json()


# put plate at position or delete plate at a location
res = requests.put(StoreURL,json={'location':'A4','plateId':'','removePlate':True})
res.status_code
res.json()


# rename a locaiton name
res = requests.put(StoreURL+'/location',json={'oldName':'A1','newName':'A11'})
res.status_code
res.json()



# query a plate

res = requests.get(StoreURL,)
res.status_code
res.json()
res = requests.get(StoreURL,json={'location':'G12'})
res.json()
from datetime import timedelta

twodayago = datetime.now() - timedelta(days=2)
 
res = requests.get(StoreURL,json={'created':{'$gt':twodayago.isoformat()}})
len(res.json())

# query all plate
res = requests.get(StoreURL,json={})
res.status_code
len(res.json())
res = requests.get(StoreURL + '/summary')

res.status_code
res.json()




# patients routes:
pRoute = 'http://localhost:8001/patients'

# get patients
res = requests.get(pRoute+'?page=0&perpage=1',json={'sampleIds':{'$elemMatch':{'$eq':"1234567890"}}})
res.status_code
res.json()

# upload patient
ps = createPatients(3)
ps[0]
res = requests.post(pRoute,json=ps[0])
res.status_code
res.json()

# delete one patient:
res = requests.delete(pRoute,)
res


# update one patients
p1 = res.json()[0]
p1.update(name='a good name',other={'desc':'a field'})
res = requests.put(pRoute,json=p1)
res.json()


# delete a patient
res = requests.delete(pRoute,json=p1)
res.json()


#Order Route

orderURL = 'http://localhost:8001/orders'

# add one order

res = requests.post(orderURL,json={'orderId':'123','meta':{'a fil':'l','b':12},
'patientIds':['123','456'],'sampleIds':['1','2'],'contact':{'p':'low','name':'a'}})
res.status_code
res.json()


# generate barcodes
barURL = 'http://ams:8001/meta/barcode'
barURL + '/?type=1&count=20'
res = requests.get(barURL + '/?type=1&count=20')
res.json() 

import base64

def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    print(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)
    
    
encode('abc','abcdefg')

decode('abc','w4LDhMOGw4XDh8OJw4g=')



