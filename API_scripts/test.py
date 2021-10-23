from connection import makeServer
import numpy as np
server = makeServer('dev')



res = server.get('/samples/id/SK00064782')

res.json()






res = server.put('/samples/sampleId',json={"sampleId":"Sk00064782","newSampleId":"SK00064782"})



res.json()



