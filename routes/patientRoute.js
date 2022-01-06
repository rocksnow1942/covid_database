const router = require('express').Router()
const Patient = require('../models/Patient')
const {DocOr400,ErrorHandler} = require('../utils/functions')


//get patients
/* 
url: /patients/?page=0&perpage=1000
Request GET: json:
Find patient with certain information:
{name:John Doe, extId: driver-license-ID }
To extract patient ID from a specific sample ID:
{'sampleIds':1234567890} patient sampleIds is an array but if one ID matches, will return the patient.
OR: {'sampleIds':{'$elemMatch':{'$eq':"1234567890"}}
Response: patient document.
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
/* 
url: /patients
Request POST: json
json can be a single patient document
or a list of several documents
response:
list of documents represent the patient.
*/
router.post('/',(req,res)=>{
    Patient.insertMany(req.body)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})

// update one patient by any field
/* 
url: /patients
request PUT: json
{
    _id: the Object ID to store patient in our database. this is used to find the patient.
    company: A company.inc,
    sampleIds:[
        sampleId1, sampleId2...
    ]
    anyother field is set to the json body.
}
TO add a new sampleId, one need to get the patient document first,
then append the new sample ID to that document,
then put the document back.
This is less ideal, but shouldn't be a bottleneck right now.
*/
router.put('/',(req,res)=>{
    Patient.findByIdAndUpdate(req.body._id,
        {$set:req.body},
        {new:true,lean:true})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

// delete patient by a given Id.
/* 
url: /patients
request DELETE json:
{
    _id: Object ID in patient database.
}
*/
router.delete('/',(req,res)=>{
    Patient.findByIdAndDelete(req.body._id)
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})




// TODO
// add sampleId to an existing patient


module.exports = router