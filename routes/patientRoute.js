const router = require('express').Router()
const Patient = require('../models/Patient')
const {DocOr400,ErrorHandler} = require('../utils/functions')


//get patients
/* 
request.body is the query filter.
*/
router.get('/',(req,res)=>{
    let page = parseInt(req.query.page) || 0
    let perpage = parseInt(req.query.perpage) || 1000
    Patient.find(req.body,null,{lean:true})
    .sort({created:-1})
    .limit(perpage)
    .skip(page*perpage)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})

// create patients
router.post('/',(req,res)=>{
    Patient.insertMany(req.body)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})

// update one patient by any field
router.put('/',(req,res)=>{
    Patient.findByIdAndUpdate(req.body._id,
        {$set:req.body},
        {new:true,lean:true})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

// delete patient by a given Id.
router.delete('/',(req,res)=>{
    Patient.findByIdAndDelete(req.body._id)
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

module.exports = router