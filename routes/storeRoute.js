const router = require('express').Router()
const Store = require('../models/Store')
const Sample = require('../models/Sample')
const {DocOr400,ErrorHandler} = require('../utils/functions')


// get the first empty location
// the empty location are returned in order.
/* 
url: /store/empty
request: GET
response: json:
{'plateId': '',
 'order': 3,
 '_id': '5fc4aaf3abfa0eb86352c59f',
 'location': 'C9',
 'created': '2020-11-30T08:18:59.433Z',
 '__v': 0}
*/
router.get('/empty',async (req,res)=>{
    Store.findOne({plateId:""},null,{sort:{order:1}})
    .then(s=>DocOr400(s,res))
    .catch(err=>ErrorHandler(err,res))    
})

// return current status of storage
/* 
url: /store/summary
resueqst GET:
response: json:
{'empty': 6, 'total': 7}
*/
router.get('/summary', async (req,res)=>{
    const total = await Store.estimatedDocumentCount()
    console.log(total)
    Store.countDocuments({plateId:""})
    .then(empty=>{
        res.json({empty,total})
    })
    .catch(err=>ErrorHandler(err,res))
})

// create new locations,add to database.
// the locations are created according to the given order. 
// this order is used to retrieve empty location.
/* 
url: /store/location
request: POST json = [{location:A1},{location:A2},...]
response:  json
[{'plateId': '',
  'order': 13,
  '_id': '5fd54a0307f61c4c8d3a484b',
  'location': 'A3',
  'created': '2020-12-12T22:53:55.697Z',
  '__v': 0},
 {'plateId': '',
  'order': 14,
  '_id': '5fd54a0307f61c4c8d3a484c',
  'location': 'A4',
  'created': '2020-12-12T22:53:55.698Z',
  '__v': 0}]
*/
router.post('/location',(req,res)=>{
    let stores = req.body;
    Store.findOne({},null,{sort:{order:-1}})
    .then(s=>{
        console.log(s);
        let order = s?s.order:0;
        stores.forEach(s=>{s.order=++order})
        return Store.insertMany(stores)
    })
    .then(docs=>DocOr400(docs,res))
    .catch(err=>ErrorHandler(err,res))
})

// update location name
/* 
url: /store/location
request PUT json: {oldName: A1 newName:A2}
response: json
{'_id': '5fd548844cd186d9231eafbc',
 'plateId': '',
 'order': 11,
 'location': 'A11',
 'created': '2020-12-12T22:47:32.769Z',
 '__v': 0}
*/
router.put('/location',async(req,res)=>{
    Store.findOneAndUpdate({location:req.body.oldName},
        {location:req.body.newName},
        {new:true,lean:true})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

// delete positions
// delete a storage position from database. 
// Also update any sample stored at this location, by set the sPlate and sWell to empty.
/* 
url: /store/location
request DELETE json: [{'location':'A5'},{'location':'E3'}]
response: json
{'modifiedSamples': {'n': 0, 'nModified': 0, 'ok': 1},
 'deletedStore': {'n': 2, 'ok': 1, 'deletedCount': 2}}
*/
router.delete('/location',(req,res)=>{
    let stores = req.body
    let result = {}
    Store.find({location:{$in:stores.map(s=>s.location)}})
    .then(docs=>{
        let nonempty = docs.filter(s=>s.plateId)
        // remove sPlate from all deleted positions in Sample collection.
        return Sample.updateMany({sPlate:{$in:nonempty.map(s=>s.plateId)}},
        {$set:{sPlate:"",sWell:""}},
        {lean:true})
    })
    .then(docs=>{
        result.modifiedSamples = docs
        return Store.deleteMany({location:{$in:stores.map(s=>s.location)}})
    })    
    .then(docs=>{
        // delete any storage position
        result.deletedStore = docs;
        res.json(result);
    })
    .catch(err=>ErrorHandler(err,res))
})

// put a plate at a position,
// is plateId is not empty, the plateId will be updated on this location.
// if plateId is empty string, then will set the the plateId at this location to empty string.
// this essentially discarded the plate from storage.
// it will also update any sample stored at this location, by setting the sPlate and sWell to empty.
// if location is not available, will return 400.
/* 
url: /store
request PUT json:
{'location':'A5','plateId':'1234567890', 'removePlate':true}
if removePlate = true, will also delete the plateId from Samples.sPlate.
response: json
{'_id': '5fc4aaf3abfa0eb86352c5a2',
 'plateId': '',
 'order': 6,
 'location': 'B2',
 'created': '2020-12-12T23:08:00.492Z',
 '__v': 0,
 'newPlateId': '123'}
FIXME:
currently, will always write the newPlateId even if the position already have old plateId.
this might cause problem; if multiple user is accessing the storage at the same time.

TODO:
when a sample storage plate is ditched, 
we can move that sample to archive to lower the sample collection space.
*/
router.put('/',(req,res)=>{
    let newPlateId = req.body.plateId || ""
    let result = {}
    Store.findOneAndUpdate({location:req.body.location},
        {$set:{plateId:newPlateId,created:Date.now()}},
        {lean:true,new:false})
    .then(doc=>{
        if (!doc) {
            res.status(400).json(doc)
        } else {
            let sPlate = doc.plateId;
            if (sPlate && req.body.removePlate) {
                // if a sample plate is found at this position,
                // and request json.removePlate  = true
                // removing the sPlate from all samples
                result.modifiedStore = doc
                Sample.updateMany({sPlate},
                    {$set:{sPlate:"",sWell:""}},
                    {lean:true})
                    .then(docs=>{
                        result.modifiedSamples = docs
                        res.json(result)
                    })
            } else {
                doc.newPlateId = newPlateId
                res.json(doc)
            }
        }
    })    
    .catch(err=>ErrorHandler(err,res))  
})


// query a plate by it's location or plateId
/* 
url: /store/?page=0&perpage=1
request GET json:
query one plateId: {plateId:}
query multiple plateId: {plateId:{$in:[id1,id2]}}
query location: {location:}
query created older than:{created:{$gt:date}}
response json:
[{'_id': '5fc4aaf3abfa0eb86352c5a2',
  'plateId': '123',
  'order': 6,
  'location': 'B2',
  'created': '2020-12-12T23:22:41.239Z',
  '__v': 0}]
*/
router.get('/',(req,res)=>{
    let page = parseInt(req.query.page) || 0
    let perpage = parseInt(req.query.perpage) || 1
    Store.find(req.body,null,{lean:true})
    .sort({created:1})
    .limit(perpage)
    .skip(page*perpage)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})




module.exports = router