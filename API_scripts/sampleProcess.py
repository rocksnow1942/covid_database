from connection import makeServer
import numpy as np
import time
server = makeServer('prod')


res = server.get('/samples',json={"meta.receptionBatchId":"61732367cac8ab2cd0c4bb77"})


len(res.json())
samples = res.json()

unknow =list( filter(lambda x: not x['meta'].get('name',None), samples))

len(unknow)

unknow[0]


a = unknow[0]

oldId = a['sampleId']
oldId
newId = oldId.replace('K','k')
newId

for a in unknow:
    oldId = a['sampleId']   
    if oldId[1] == 'k':
        newId = oldId.replace('k','K')
        print(oldId,newId)
        u = server.put('/samples/sampleId',json={"sampleId":oldId, "newSampleId":newId })        
        time.sleep(0.2)

u = server.put('/samples/sampleId',json={"sampleId":"SK00122020", "newSampleId":"Sk00122020" })
    
    
u.json()