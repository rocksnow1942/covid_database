const router = require('express').Router()
const Store = require('../models/Store')
const Sample = require('../models/Sample')
const {DocOr400,ErrorHandler} = require('../utils/functions')


// get the first empty position
router.get('/empty',async (req,res)=>{
    Store.findOne({plateId:""},null,{sort:{order:1}})
    .then(s=>DocOr400(s,res))
    .catch(err=>ErrorHandler(err,res))    
})

// create new position
/* 
format must be: a list of position names:
{
    location: location name.
}
*/
router.post('/location',(req,res)=>{
    let stores = req.body;
    Store.findOne({},null,{sort:{order:1}})
    .then(s=>{
        let order = s?s.order:0;
        stores.forEach(s=>{s.order=++order})
        return Store.insertMany(stores)
    })
    .then(docs=>DocOr400(docs,res))
    .catch(err=>ErrorHandler(err,res))
})

// update location name
/* 
request body format:
{oldName: newName:}
*/
router.put('/location',async(req,res)=>{
    Store.findOneAndUpdate({location:req.body.oldName},
        {location:req.body.newName},
        {new:true,lean:true})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

// delete positions
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

// put a plate at a position, if plateId is empty string, then will remove it.
/* 
request body: {
    plateId:"123",
    location: 'location name' // if location is not provided, set it to empty string.
}
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
            if (sPlate && !newPlateId) {
                // removing the sPlate from all samples
                result.modifiedStore = doc
                Sample.updateMany({sPlate},
                    {$set:{sPlate:"",sWell:""}},
                    {lean:true})
                    .then(docs=>{
                        result.modifiedSamples = docs
                        res.json(result)
                    })
            } else if (!sPlate && newPlateId){
                doc.newPlateId = newPlateId
                res.json(doc)
            }
            else {
                res.status(400).json({sPlate,newPlateId,doc})
            }
        }
    })    
    .catch(err=>ErrorHandler(err,res))
    
})


// query a plate by it's location or plateId
/* 
query one plateId: {plateId:}
query multiple plateId: {plateId:{$in:[id1,id2]}}
query location: {location:}
query created older than:{created:{$gt:date}}
*/
router.get('/',(req,res)=>{
    Store.find(req.body,null,{lean:true})
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})


module.exports = router