# scripts for process plate reuslt in the mongodb.


from connection import makeServer
import numpy as np
server = makeServer('prod')



res = server.get('/plates/?page=0&perpage=1000')

plates = res.json()

len(plates)
plates[0]['wells']
plates[0]['plateId']
plates[0]['result']

def calcMetrics(wells, labels):
        "calculate average, cv"
        vals = [wells[l]['raw'] for l in labels]
        return round(np.mean(vals), 1), round(np.std(vals, ddof=1)*100/(max(np.mean(vals),1e-6)), 2),

def calcRatioGenerator(NBCavg, PTCavg):
       def wrap(raw):
           return round((raw-NBCavg)/ (max((PTCavg-NBCavg),1e-6)) * 9 + 1, 2)
       return wrap


def calcPlateResult(plate):
    layout = plate['layout']
    wells = plate['wells']
    primer = 'RP4' if layout.endswith('RP4Ctrl') else 'N7'
    NTCavg, NTCcv = calcMetrics(wells, ['A12', 'B12'])
    PTCavg, PTCcv = calcMetrics(wells, ['C12', 'D12', 'E12'])
    NBCavg, NBCcv = calcMetrics(wells, ['F12', 'G12', 'H12'])
    calc = calcRatioGenerator(NBCavg, PTCavg)     
    return {
        f'{primer}_NTC_Avg': round(NTCavg,2),
        f'{primer}_PTC_Avg': round(PTCavg,2),
        f'{primer}_NBC_Avg': round(NBCavg,2),
        f'{primer}_NTC': calc(NTCavg),
        f'{primer}_NTC_CV': NTCcv,
        f'{primer}_PTC': round(PTCavg/(max(NBCavg,1e-6)), 2),
        f'{primer}_PTC_CV': PTCcv,
        f'{primer}_NBC_CV': NBCcv,
    }
     
calcPlateResult(plates[0]) 

updateResult = [{'plateId':i['plateId'], 'result':calcPlateResult(i)} for i in plates]
updateResult[0]

# write back to server
for update in updateResult:
    res = server.put('/plates',json=update)
    print(f'Update {update["plateId"]}',res.status_code)



