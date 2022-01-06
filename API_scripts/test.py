from connection import makeServer
import numpy as np
server = makeServer('dev')



res = server.get('/samples/id/SK00064782')

res.json()






res = server.put('/samples/sampleId',json={"sampleId":"Sk00064782","newSampleId":"SK00064782"})



res.json()



import re



p = re.compile('^(SK)?\d{8}$')

print(f"Match {p.match('SK12345121')}")

print(f"Match {p.match('12345120')}")