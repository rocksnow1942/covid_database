const router = require('express').Router()
const Order = require('../models/Order')
const {DocOr400,ErrorHandler} = require('../utils/functions')



// get orders
/* 
url: /orders/?page=0&perpage=10
Request GET:json
Return order document json.
*/
router.get('/',(req,res)=>{
    let page = parseInt(req.query.page) || 0
    let perpage = parseInt(req.query.perpage) || 10
    Patient.find(req.body,null,{lean:true})
    .sort({created:-1})
    .limit(perpage)
    .skip(page*perpage)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})


//create order
/* 
url: /orders
Request POST: json
json can be a single doc or list of docs
document represent the order.
*/
router.post('/',(req,res)=>{
    Order.insertMany(req.body)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})

// update one order by any field
/* 
url: /orders
request PUT: json
{
    _id: the Object ID to store order in our database.
    anyother field is used to update the document.
}
*/
router.put('/',(req,res)=>{
    Order.findByIdAndUpdate(req.body._id,
        {$set:req.body},
        {new:true,lean:true})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})


// delete order by a given Id.
/* 
url: /orders
request DELETE json:
{
    _id: Object ID in order database.
}
*/
router.delete('/',(req,res)=>{
    Order.findByIdAndDelete(req.body._id)
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

module.exports = router