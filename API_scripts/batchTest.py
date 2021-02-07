"""
for making batch upload csv files
"""
from connection import makeServer
from datetime import datetime
from dateutil import tz
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
    2021, 2, 5, 9, 13).astimezone(tz.tzlocal()).astimezone(tz.UTC).isoformat()}})

sampleIds = [i['sampleId'] for i in res.json()]


# save the file to accession csv file
makeAccessionCsv(sampleIds)











