report_CSV_headers=['collection_date_yyyymmdd',
 'accession_id',
 'patient_middle_name',
 'mrn',
 'patient_first_name',
 'patient_last_name',
 'patient_dob_yyyymmdd',
 'patient_gender',
 'patient_race',
 'patient_ethnicity',
 'patient_address',
 'patient_city',
 'patient_state',
 'patient_zip',
 'patient_phone',
 'patient_email',
 'gender_identity',
 'sex_assigned_at_birth',
 'sexual_orientation',
 'physician_first_name',
 'physician_last_name',
 'npi',
 'client_name',
 'client_address',
 'client_city',
 'client_state',
 'client_zip',
 'client_country',
 'client_phone_number',
 'billing_type',
 'insurance_company_1',
 'policy_num_1',
 'group_num_1',
 'first_name_of_primary_insured_1',
 'last_name_of_primary_insured_1',
 'relationship_to_patient_1',
 'insurance_company_2',
 'policy_num_2',
 'group_num_2',
 'first_name_of_primary_insured_2',
 'last_name_of_primary_insured_2',
 'relationship_to_patient_2',
 'first_test',
 'employed_in_healthcare_setting',
 'symptomatic',
 'date_of_onset',
 'hospitalized',
 'icu',
 'resident_in_congregate_care_setting',
 'pregnant']



report_required=[
 'collection_date_yyyymmdd',
 'accession_id',
 'patient_first_name',
 'patient_last_name',
 'patient_dob_yyyymmdd',
 'patient_gender',
 'patient_race',
 'patient_ethnicity',
 'patient_address',
 'patient_city',
 'patient_state',
 'patient_zip',
 'physician_last_name',
 'physician_first_name',
 'client_name',
 'npi',
"client_address",
"client_city",
"client_state",
"client_zip",
"client_phone_number",
]

import random

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
        'test patient address',
        'Goleta',
        'CA',
        '93117',
        'TEST',
        'PHYSICIAN',
        'TEST CLIENT NAME',
        'TEST PHYSICIAN NPI',
        'M/S 7002',
        'Santa barbara',
        'CA',
        '93106-7002',
        '805-935-5339',        
    ]
    return dict(zip(report_required, data))


def generateCSV(n, file):
    "generate upload csv, this is the ucsb format."
    rows = [','.join(report_CSV_headers)]
    for i in range(n):
        row = []
        p = generatePatient(i)
        for c in report_CSV_headers:
            row.append(p.get(c, ''))
        rows.append(','.join(row))
    with open(file, 'wt') as f:
        f.write('\n'.join(rows))
    return