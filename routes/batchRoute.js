const router = require('express').Router()
const Batch = require('../models/Batch')
const {DocOr400,ErrorHandler} = require('../utils/functions')



// get batch data
/* 
url: /batch/?page=0&perpage=10
Request GET:json
Return batch document json.
*/
router.get('/',(req,res)=>{
    let page = parseInt(req.query.page) || 0
    let perpage = parseInt(req.query.perpage) || 10
    Batch.find(req.body,null,{lean:true})
    .sort({created:-1})
    .limit(perpage)
    .skip(page*perpage)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})


//create order
/* 
url: /batch
Request POST: json
json can be a single doc or list of docs
document represent the order.
*/
router.post('/',(req,res)=>{
    Batch.insertMany(req.body)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})

// update one order by any field
/* 
url: /batch
request PUT: json
{
    _id: the Object ID to store order in our database.
    anyother field is used to update the document.
}
*/
router.put('/',(req,res)=>{
    Batch.findByIdAndUpdate(req.body._id,
        {$set:req.body},
        {new:true,lean:true})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})


// delete order by a given Id.
/* 
url: /batch
request DELETE json:
{
    _id: Object ID in order database.
}
*/
router.delete('/',(req,res)=>{
    Batch.findByIdAndDelete(req.body._id)
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

module.exports = router