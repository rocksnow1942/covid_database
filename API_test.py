import requests
import random 
from bson.objectid import ObjectId
import time
from datetime import datetime

import dateutil.parser
from dateutil import tz

def parseISOTime(ts):
    dt = dateutil.parser.parse(ts)
    return dt.astimezone(tz.tzlocal())

def IDgen():
    return f"{int(random.random()*1e10):010d}"

def randWell():
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

def postSamples(samples):
    
    res = requests.post(URL+'/samples',json = samples)


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
    


# Test Sample Route
URL = 'http://localhost:8001'
samples = createSamples(96)

# get samples
res = requests.get(URL+'/samples?page=0&perpage=1000000',)
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
    samples = createSamples(9600)
    res = requests.post(URL+'/samples',json = samples)
t1 = time.perf_counter()-t0
print(t1)
len(res.json())
res.json()[0]
res.status_code
updateSample = samples[0:3]

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
samples[4:10]
putres = requests.put(URL+'/samples',json=samples[4:10])
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
upres = requests.post(URL+'/samples/upsert',json=oldsample+newsample)
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
res = requests.delete(URL+'/samples',json=[{'sampleId':IDgen()} for i in range(5)])
res.status_code
res.json()

# append results
res = requests.post(URL+'/samples/results',json=samples[0:3])
res.json()



# test Plate route
PlateURL = 'http://localhost:8001/plates'

# get new plate
res = requests.get(PlateURL+'/?page=0&perpage=10',json={'plateId':'6125506475'})
res.status_code
res.json()

# get one plate
res = requests.get(PlateURL+'/id/6125506475',json={'plateId':'6125506475'})
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

# link plate
oldId = plate2['plateId']
res = requests.put(PlateURL+'/link',json={'oldId':plate2['plateId'],'newId':IDgen(),'step':'lamp'})
oldId
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
positions = [{'location':randWell()} for i in range(10)]

positions
res = requests.post(StoreURL+'/location',json=positions)
res.status_code
res.json()


# delete positions
positions = [{'location':randWell()} for i in range(1000)]
res = requests.delete(StoreURL + '/location',json=positions)
res.json()


# put plate at position or delete plate at a location
res = requests.put(StoreURL,json={'location':'G12','plateId':'12'})
res.status_code
res.json()



# rename a locaiton name
res = requests.put(StoreURL+'/location',json={'oldName':'G10','newName':'G12'})
res
res.json()


# query a plate
res = requests.get(StoreURL,json={'plateId':{'$in':['a plate id','12']}})
res.status_code
res.json()
res = requests.get(StoreURL,json={'location':'G12'})
res.json()
from datetime import timedelta

twodayago = datetime.now() - timedelta(days=2)

twodayago.isoformat()

t = datetime.now().isoformat()
t

res = requests.get(StoreURL,json={'created':{'$gt':twodayago.isoformat()}})
len(res.json())



