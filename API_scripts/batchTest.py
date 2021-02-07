"""
for making batch upload csv files
"""
from connection import makeServer,Firebase
from datetime import datetime
import random
from dateutil import tz,parser

fire = Firebase(username='admin@ams.com',password='password',url='https://us-central1-ams-clia.cloudfunctions.net/api')
fire.start()
server = makeServer('prod')


header = "collection_date_yyyymmdd,accession_id,patient_middle_name,mrn,\
patient_first_name,patient_last_name,patient_dob_yyyymmdd,patient_gender,\
patient_race,patient_ethnicity,patient_address,patient_city,patient_state,\
patient_zip,patient_phone,patient_email,gender_identity,sex_assigned_at_birth,\
sexual_orientation,physician_first_name,physician_last_name,npi,client_name,\
client_address,client_city,client_state,client_zip,client_country,client_phone_number,\
billing_type,insurance_company_1,policy_num_1,group_num_1,first_name_of_primary_insured_1,\
last_name_of_primary_insured_1,relationship_to_patient_1,insurance_company_2,policy_num_2,\
group_num_2,first_name_of_primary_insured_2,last_name_of_primary_insured_2,relationship_to_patient_2,\
first_test,employed_in_healthcare_setting,symptomatic,date_of_onset,\
hospitalized,icu,resident_in_congregate_care_setting,pregnant"

row="""20201103,NF127413841,R.H,726974,TEST01,PATIENT,19881216,M,\
WHI,NAM,123 GOLETA AVE,SANTA BARBARA,CA,93106,555-555-5555,TEST01PATIENT@ucsb.edu,\
M,M,O,LAURA,POLITO,1629173778,UCSB Student Health Service,M/S 7002,Santa Barbara,\
CA,93106-7002,US,805-935-5339,Institution,,,,,,,,,,,,,N,N,N,,N,N,N,U""".split(',')
 
 

def parseISOTime(ts):
    "turn mongo time stamp to python datetime object."
    dt = parser.parse(ts)
    return dt.astimezone(tz.tzlocal())

def generateId(n=96,seed=40):
    random.seed(seed)
    return [f'MK{random.random()*1e9:.0f}' for i in range(n)]
    
    


def makeAccessionCsv(sampleIds,file='./accession.csv'):
    rows = [header]
    for idx,id in enumerate(sampleIds):
        row[1] = id
        row[3] = str(int(row[3]) +1)
        row[4] = f"Jon-{idx}"
        row[5] = f"Doh-{idx}"
        rows.append(','.join(row))
    with open(file,'wt') as f:
        f.write('\n'.join(rows))
    

# get samples created after certain time.
res = server.get('/samples', json={'created': {'$gt': datetime(
    2021, 2, 7, 9, 13).astimezone(tz.tzlocal()).astimezone(tz.UTC).isoformat()}})

sampleIds = [i['sampleId'] for i in res.json()]
len(sampleIds)

# save the file to accession csv file
makeAccessionCsv(sampleIds)





# generage some Id and mimick the create Sample routine

sampleIds = generateId()

res = server.get('/samples',json={'sampleId':{'$in':sampleIds}})
print(res.status_code)
validexist = []
conflict = []
for s in res.json():
    if s.get('meta',{}).get('from',None)=='appCreated' and (not s.get('sPlate',None)):
        validexist.append(s.get('sampleId'))
    else:
        conflict.append(s.get('sampleId'))

len(validexist)
validexist

# mimic create sampleIds in mongodb by create sample routine
res = server.post('/samples',json=[{'sampleId':id,'receivedAt':datetime.now().isoformat()} for id in sampleIds[0:50]])
res.json()[0]

# mimic update existing sampleIds in mongodb by create sample routine
res = server.put('/samples',json=[{'sampleId':id,'receivedAt':datetime.now().isoformat()} for id in validexist])


# mimic load samples onto lyse plate and scan
res = server.put('/samples',json=[{'sampleId':id,'sPlate':'0000000000',}  for id in sampleIds] )
res.status_code
res.json()[0]

sampleIds


# delete samples from mongodb
res = server.delete('/samples',json=[{'sampleId':id} for id in sampleIds])
res.json()




# fetch batch from firebase

res = fire.post('/data/querydetails',json={'field':'batchID','op':'==','value':'soKy2d71kreeD4DQtctm',"collection":['UCSB']})
res.status_code
data = res.json()
data[0]


# delete data from firebase
toDeletDoc = res.json()
res = fire.delete('/data',json=[i['_docID'] for i in toDeletDoc])
res.status_code
res.json()



