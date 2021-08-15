import json
from datetime import datetime
from dateutil import parser
import pandas as pd
import numpy as np
from firebaseClient import Firebase

firebase = Firebase(username='jskanghui@gmail.com')


def parseCSV(file):
    "read and return structured data from CSV file."
    with open(file, 'rt') as f:
        data = f.readlines()
    id = ""
    wells = {}
    wellStart = False
    handler = 'admin'
    for line in data:
        if wellStart:
            ss = line.strip().split(',')
            if len(ss) != 2 or (not ss[1]):
                continue
            well, value = ss
            # turn A01 to A1
            well = f"{well[0]}{int(well[1:])}"
            wells[well] = int(float(value))
        elif line.startswith('ID'):
            id = line.strip().split(',')[1]
        elif line.startswith('Created By User'):
            handler = line.strip().split(',')[1] or handler
        elif line.startswith('Well,'):
            wellStart = True
    return id, wells, handler


def calcMetrics(wells, labels):
    "calculate average, cv"
    vals = [wells[l] for l in labels]
    return round(np.mean(vals), 1), round(np.std(vals, ddof=1)*100/(max(np.mean(vals), 1e-6)), 2),


def calcRatioGenerator(NBCavg, PTCavg):
    def wrap(raw):
        return round((raw-NBCavg) / (max((PTCavg-NBCavg), 1e-6)) * 9 + 1, 2)
    return wrap


def calcPlate(primer, wells):
    """
    return the ratio of each well, and the control meta information
    """
    NTCavg, NTCcv = calcMetrics(wells, ['A12', 'B12'])
    PTCavg, PTCcv = calcMetrics(wells, ['C12', 'D12', 'E12'])
    NBCavg, NBCcv = calcMetrics(wells, ['F12', 'G12', 'H12'])
    calc = calcRatioGenerator(NBCavg, PTCavg)
    result = {}
    for well, raw in wells.items():
        result[well] = calc(raw)
    return result, {
        f'{primer}_NTC_Avg': round(NTCavg, 2),
        f'{primer}_PTC_Avg': round(PTCavg, 2),
        f'{primer}_NBC_Avg': round(NBCavg, 2),
        f'{primer}_NTC': calc(NTCavg),
        f'{primer}_NTC_CV': NTCcv,
        f'{primer}_PTC': round(PTCavg/(max(NBCavg, 1e-6)), 2),
        f'{primer}_PTC_CV': PTCcv,
        f'{primer}_NBC_CV': NBCcv,
    }


def writeWellsToCSV(wells, file):
    """
    write a dictionary of well values to a 9X12 column csv file
    """
    data = []
    for r in 'ABCDEFGH':
        row = {}
        for col in range(1, 13):
            row[col] = wells[f"{r}{col}"]
        data.append(row)
    df = pd.DataFrame(data, index=list('ABCDEFGH'))
    df.to_csv(file)


def readWellsCSV(file):
    df = pd.read_csv('test.csv', index_col=0).dropna(how='all')
    wells = {}
    for l, r in df.iterrows():
        for c in r.index:
            wells[f"{l}{c}"] = r[c]
    return wells


def readIDfile(file):
    df = pd.read_csv(file).fillna('')
    data = df.to_dict(orient='list')
    return {i: j for i, j in zip(data['Well'], data['ID']) if j}


def callResult(res, NTCs):
    """
    call based on individual well result
    """
    if any([i > 5 for i in NTCs['N7']]):
        return 'Invalid:N7NTC'
    if any([i > 5 for i in NTCs['RP4']]):
        return 'Invalid:RP4NTC'
    if res['N7_NBC_CV'] > 5:
        return 'Invalid:N7CV'
    if res['RP4_NBC_CV'] > 5:
        return 'Invalid:RP4CV'
    if res['N7_PTC'] < 1.7:
        return 'Invalid:N7PTC'
    if res['RP4_PTC'] < 1.7:
        return 'Invalid:RP4PTC'
    if res['N7'] > 5:
        return 'Positive'
    if res['RP4'] < 5:
        return 'Invalid:RP4'
    return 'Negative'


def utcTime(t=None):
    return parser.parse(t or str(datetime.utcnow())).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z'


def calcResultRecords(N7file, RP4file, N7control, RP4control, IDfile, plateID, testStart, testEnd, receivedAt):
    """
    Inputs:
    N7file/RP4file: N7/RP4 plate ratio result, from writeWellsToCSV,
    N7control, RP4control: control meta information, from calcPlate,
    IDfile: sampleId information on each well, from PiScanner generated csv file.
    plateID: plate ID to report to cloud.
    testStart: test start time.
    testEnd: test end time.
    receivedAt: when we receive the samples.
    """
    N = readWellsCSV(N7file)
    RP = readWellsCSV(RP4file)
    wells = readIDfile(IDfile)
    control = dict(list(N7control.items()) + list(RP4control.items()))
    NTCs = {n: [i[w] for w in ['A12', 'B12']]
            for (n, i) in [('N7', N), ('RP4', RP)]}
    results = []
    for well, ID in wells.items():
        n = N[well]
        r = RP[well]
        control.update(N7=n, RP4=r, sampleId=ID,
                       plateId=plateID,
                       testStart=utcTime(testStart),
                       testEnd=utcTime(testEnd),
                       comment="",
                       receivedAt=receivedAt,
                       type='saliva',
                       )
        control.update(result=callResult(control, NTCs))
        results.append(control)
    return results


def linkBookingToResult(bookingfile, results):
    "link booking details do"


class Analyzer:
    def __init__(self, N7, RP4):
        self.rawDataFile = dict(N7=N7, RP4=RP4)
        self.controlMeta = {}
        self.ratioDataFile = {i: '.'.join(
            f.split('.')[:-1]) + '_ratio.csv' for i, f in self.rawDataFile.items()}
        self.reportFile = '.'.join(N7.split('.')[:-1]) + '_report.csv'
        self.report = []
        self.reportHeader = []
        self.toUpload = []

    def parseToRatio(self):
        for p, f in self.rawDataFile.items():
            _, wells, _ = parseCSV(f)
            w, c = calcPlate(p, wells)
            writeWellsToCSV(w, self.ratioDataFile[p])
            self.controlMeta[p] = c

    def generateReport(self, IDfile, bookFile, plateID, testStart, testEnd, receivedAt):
        result = pd.DataFrame(calcResultRecords(
            self.ratioDataFile['N7'],
            self.ratioDataFile['RP4'],
            self.controlMeta['N7'],
            self.controlMeta['RP4'],
            IDfile,
            plateID,
            testStart, testEnd, receivedAt
        ))
        self.reportHeader = list(result.columns) + ['ID']
        result = result.set_index('sampleId')
        book = pd.read_csv(bookFile).fillna('').dropna(how='all')
        records = book.join(result, on='Sample ID', how='outer')
        records.to_csv(self.reportFile, index=False)

    def readReportFromCSV(self):
        df = pd.read_csv(
            self.reportFile, usecols=self.reportHeader).dropna(how='any')
        self.toUpload = df.to_dict(orient='records')
        print(f'toUpload = {len(self.toUpload)} patients')
        print(json.dumps(self.toUpload[0:3], indent=2))

    def uploadToCloud(self):
        """
        upload to cloud.
        1. use the ID to fetch record from cloud, and get the collection_date_yyyymmdd.
        2. upload test results, physician info changes to cloud.
        """
        ans = input(
            f'Confirm uploading {len(self.toUpload)} patients... [yes/no]')
        if ans != 'yes':
            return
        for idx, doc in enumerate(self.toUpload):
            id = doc['ID']
            data = doc.copy()
            data.pop('ID')
            res = firebase.get(f'/data{id}')
            if res.status_code != 200:
                raise Exception(f'{id} not found in cloud; {res.text}')
            data['collectAt'] = res.json(
            )['patientInfo']['collection_date_yyyymmdd']
            packet = {'details': data, 'resultAt': utcTime(
            ), "approved": False, 'sent': False, 'read': False}
            packet['patientInfo.physician_first_name'] = "Michael"
            packet['patientInfo.physician_last_name'] = "Bauer"
            packet['patientInfo.client_name'] = "Aptitude Medical Systems"
            packet['patientInfo.npi'] = "1346417086"
            packet['patientInfo.client_address'] = "125 Cremona Drive"
            packet['patientInfo.client_city'] = "Goleta"
            packet['patientInfo.client_state'] = "CA"
            packet['patientInfo.client_zip'] = "93117"
            packet['patientInfo.client_phone_number'] = "805-409-9669"
            res = firebase.put(f'/data{id}', json=packet)
            if res.status_code != 200:
                raise Exception(f'{id} not uploaded to cloud; {res.text}')
            print(f'{idx}/{len(self.toUpload)} {id} uploaded to cloud; {res.text}')


"""
======================================================================
Step 1. Read raw data from bioRad CFX 96 
parse and export ratio data in plate format csv file.
The file is saved as 'originnal_filename_ratio.csv'
Check the ratio file, place values if needed
======================================================================
"""
analyzer = Analyzer(
    N7="N7file",  # N7 raw data from CFX96
    RP4="RPfile",  # RP4 raw data from CFX96
)

analyzer.parseToRatio()


"""
======================================================================
Step 2. Re-read the ratio file after adjustment.
Calculate the results and generate result records to upload.
Save the records to a csv file. Proofread the csv file before proceed.
======================================================================
"""
analyzer.generateReport(
    IDfile='',  # well label - sample ID csv file, generated from Pi scanner
    bookFile='',  # booking CSV file, from CUBE booking page. only Require ID and sample ID fields, other fields optional
    plateID='',  # sample Plate ID, can use a random 10digit number
    testStart='',  # test Start time, use YYYY-MM-DD HH:mm:ss format
    testEnd='',  # test End time, use YYYY-MM-DD HH:mm:ss format
    receivedAt='',  # When we received the sample, use YYYY-MM-DD HH:mm:ss format
)


"""
======================================================================
Step 3. Read the records from csv file and upload to cloud.
The report file is generated by the function above. 
If a row have any field missing, this record is not uploaded.
======================================================================
"""
analyzer.readReportFromCSV()

analyzer.uploadToCloud()
