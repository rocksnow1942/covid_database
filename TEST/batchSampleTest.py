"""
TEST SUIT for checking enterprise customer submit CSV to our website,
then send samples to us,
we login the samples and send result report.
"""

from datetime import datetime
from connection import makeServer
import random
from testUtils import generateCSV

"""
 ██████╗███████╗██╗   ██╗    ███████╗██╗██╗     ███████╗
██╔════╝██╔════╝██║   ██║    ██╔════╝██║██║     ██╔════╝
██║     ███████╗██║   ██║    █████╗  ██║██║     █████╗  
██║     ╚════██║╚██╗ ██╔╝    ██╔══╝  ██║██║     ██╔══╝  
╚██████╗███████║ ╚████╔╝     ██║     ██║███████╗███████╗
 ╚═════╝╚══════╝  ╚═══╝      ╚═╝     ╚═╝╚══════╝╚══════╝                                                    
Generate CSV file for upload.
The sample ID is 'TEST{i:06}'
"""


generateCSV(100, "C:/Users/hui/Desktop/TEST_SAMPLES.csv")


"""
 █████╗  ██████╗ ██████╗███████╗███████╗███████╗██╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝██║██╔═══██╗████╗  ██║
███████║██║     ██║     █████╗  ███████╗███████╗██║██║   ██║██╔██╗ ██║
██╔══██║██║     ██║     ██╔══╝  ╚════██║╚════██║██║██║   ██║██║╚██╗██║
██║  ██║╚██████╗╚██████╗███████╗███████║███████║██║╚██████╔╝██║ ╚████║
╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
Simulate we got the sample from enterprise client and scan the barcode. 
The sample ID from the csv generated above is 'TEST{i:06}'
"""


server = makeServer('prod')
server.setUser({'username': 'UNIT_TEST'})
# 60384b1939e2561f208593a3 is the default test batch
testBatchID = '60384b1939e2561f208593a3'

# simulate we received 95 samples, instead of 100 samples.
# 90 samples from CSV uploaded are send to us and scanned,
# 5 samples are mistakenly scanned wrong.  (100-104)
# 5 samples are missing. (90-99)
sampleIds = [f"TEST{i:06}" for i in range(
    90)] + [f"TEST{i:06}" for i in range(100, 105)]


# check with database to see if samples already exist .
existCheckRes = server.get('/samples', json={'sampleId': {'$in': sampleIds}})
validexist = []
conflict = []
for s in existCheckRes.json():
    if s.get('meta', {}).get('from', None) == 'appCreated' and (not s.get('sWell', None)):
        validexist.append(s.get('sampleId'))
    else:
        conflict.append(s.get('sampleId'))
        
print(f'{len(validexist)} samples already in mongodb, created by App.')

if conflict:
    raise RuntimeError('Some samples have conflict.')


# update the batch document with new sample count;
batchRes = server.post(
    '/batch/addsample', json={'id': testBatchID, 'count': len(sampleIds)})


# if sample is already pulled down, should update instead of create new.
sampleUpdateRes = server.put('/samples', json=[{'sampleId': id, 'receivedAt': datetime.now().isoformat(),
                                                'sWell': f'Well-{id}', 'meta.receptionBatchId': testBatchID, 'meta.handler': 'UNIT_TEST'} for id in validexist])

# create new samples with a specific batchID ; this is simulating the batch order is not
# pulled down from firebase and we are creating new samples.
# because the user is set by server request header in the post routine, no need to add hander.
sampleCreateRes = server.post('/samples', json=[{'sampleId': id, 'receivedAt': datetime.now().isoformat(),
                                                 'sWell': f'Well-{id}', 'meta': {"receptionBatchId": testBatchID}} for id in sampleIds if id not in validexist])


print(f'New count in Batch Record {batchRes.json()["receivedCount"]}')
print(f'Created {len(sampleCreateRes.json())} samples.')
print(f'Updated {len(sampleUpdateRes.json())} samples.')



"""
██╗      █████╗ ███╗   ███╗██████╗ 
██║     ██╔══██╗████╗ ████║██╔══██╗
██║     ███████║██╔████╔██║██████╔╝
██║     ██╔══██║██║╚██╔╝██║██╔═══╝ 
███████╗██║  ██║██║ ╚═╝ ██║██║     
╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     
Simulate our testing routine and generate result.
"""


server = makeServer('prod')
server.setUser({'username': 'UNIT_TEST'})

# simulate 90 samples from CSV uploaded are send to us and scanned,
# 5 samples are mistakenly scanned wrong.  (100-104)
# 5 samples are missing. (90-99)
sampleIds = [f"TEST{i:06}" for i in range(
    90)] + [f"TEST{i:06}" for i in range(100, 105)]

# mimic load samples onto lyse plate and scan
createPlateRes = server.put('/samples', json=[{'sampleId': id, 'sPlate': f"TEST_sPLATE{i:04}", }
                                   for (i, id) in enumerate(sampleIds)])

# mimic run test on 2 plates.
createN7PlateRes = server.post('/plates', json={"plateId": 'TEST_N7_PLATE', "step": 'read',
                                                'layout': 'variableSample_2NTC_3PTC_3IAB', 'companion': 'TEST_RP4_PLATE'})

createRP4PlateRes = server.post('/plates', json={"plateId": 'TEST_RP4_PLATE', "step": 'read',
                                                 'layout': 'variableSample_2NTC_3PTC_3IAB-RP4Ctrl', "companion": 'TEST_N7_PLATE'})


# mimic produce result:
random.seed(42)
results = [{'sampleId': id, 'results': [{
    "result": random.choice(['Positive', 'Negative']),
    'plateId':['TEST_N7_PLATE', 'TEST_RP4_PLATE'],
    "testStart":datetime.now().isoformat(),
    "N7": 1,
    "N7_NTC":1,
    "N7_PTC":2,
    "N7_NTC_CV":1,
    "N7_PTC_CV":1,
    "N7_NBC_CV":1,
    "RP4": 10,
    "RP4_NTC":1,
    "RP4_PTC": 2,
    "RP4_NTC_CV":1,
    "RP4_PTC_CV":1,
    "RP4_NBC_CV":1,
}]} for id in sampleIds]

addResultRes = server.post('/samples/results', json=results)
print(f'Write sPlate ID to {len(createPlateRes.json())} samples.')
print(f'Created plate {createN7PlateRes.json()["plateId"]}.')
print(f'Created plate {createRP4PlateRes.json()["plateId"]}.')
print(f'Added Fake Result to {len(addResultRes.json())} samples.')




"""
 ██████╗██╗     ███████╗ █████╗ ███╗   ██╗██╗   ██╗██████╗ 
██╔════╝██║     ██╔════╝██╔══██╗████╗  ██║██║   ██║██╔══██╗
██║     ██║     █████╗  ███████║██╔██╗ ██║██║   ██║██████╔╝
██║     ██║     ██╔══╝  ██╔══██║██║╚██╗██║██║   ██║██╔═══╝ 
╚██████╗███████╗███████╗██║  ██║██║ ╚████║╚██████╔╝██║     
 ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     
Clean up test traces when done.
"""

sampleIds = [f"TEST{i:06}" for i in range(
    100)] + [f"TEST{i:06}" for i in range(100, 105)]

plateIds = ['TEST_N7_PLATE','TEST_RP4_PLATE']

delSampleRes = server.delete('/samples',json=[{'sampleId':id} for id in sampleIds])
print(f'Deleted samples {delSampleRes.json()}')

for id in plateIds:
    delPlateRes = server.delete('/plates',json={'plateId':id})
    print(f"Deleted Plate {id} Res {delPlateRes.json()}")







