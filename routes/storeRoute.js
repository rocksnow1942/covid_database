const router = require('express').Router()
const Store = require('../models/Store')
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
    Store.deleteMany({location:{$in:stores.map(s=>s.location)}})
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})

// put a plate at a position, if plateId is empty string, then will remove it.
/* 
request body: {
    plateId:"123",
    location: 'location name'
}
*/
router.put('/',(req,res)=>{
    Store.findOneAndUpdate({location:req.body.location},
        {$set:{plateId:req.body.plateId,created:Date.now()}},
        {new:true,lean:true})
    .then(doc=>DocOr400(doc,res))
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