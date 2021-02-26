"""
TEST SUIT for checking enterprise customer submit CSV to our website,
then send samples to us,
we login the samples and send result report.
"""


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




from datetime import datetime
from connection import makeServer
import random
from batchSampleTest import report_CSV_headers as headers
from batchSampleTest import report_required as required
def generatePatient(i):
    "generate a random patient with requried information."
    data = [
        '20210101',
        f'TEST{i:06}',
        f"John{i}",
        f"Doe{i}",
        "20001230",
        random.choice('FM'),
        random.choice('ABPSWO'),
        random.choice('HNU'),
        'patient address',
        'Goleta',
        'CA',
        '93117',
    ]
    return dict(zip(required, data))


def generateCSV(n, file):
    "generate upload csv, this is the ucsb format."
    rows = [','.join(headers)]
    for i in range(n):
        row = []
        p = generatePatient(i)
        for c in headers:
            row.append(p.get(c, ''))
        rows.append(','.join(row))
    with open(file, 'wt') as f:
        f.write('\n'.join(rows))
    return


generateCSV(100, './dummpyAptitudeUpload.csv')


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
# simulate 90 samples from CSV uploaded are send to us and scanned,
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
if conflict:
    raise RuntimeError('Some samples have conflict.')


# update the batch document with new sample count;
batchRes = server.post(
    '/batch/addsample', json={'id': testBatchID, 'count': len(sampleIds)})


# if sample is already pulled down, should update instead of create new.
sampleUpdateRes = server.put('/samples', json=[{'sampleId': id, 'receivedAt': datetime.now().isoformat(),
                                                'sWell': f'Well-{id}', 'meta.receptionBatchId': testBatchID, 'meta.handler': 'Hui'} for id in validexist])

# create new samples with a specific batchID ; this is simulating the batch order is not
# pulled down from firebase and we are creating new samples.
# because the user is set by server request header in the post routine, no need to add hander.
sampleCreateRes = server.post('/samples', json=[{'sampleId': id, 'receivedAt': datetime.now().isoformat(),
                                                 'sWell': f'Well-{id}', 'meta': {"receptionBatchId": testBatchID}} for id in sampleIds if id not in validexist])


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
    90)] + [f"TEST{i:06}" for i in range(100, 105)]

plateIds = ['TEST_N7_PLATE','TEST_RP4_PLATE']

delSampleRes = server.delete('/samples',json=[{'sampleId':id} for id in sampleIds])

delPlateRes = server.delete('/plates',json=[{'plateId':id} for id in plateIds])
