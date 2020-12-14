const router = require('express').Router()
const Plate = require('../models/Plate')

const {DocOr400,ErrorHandler} = require('../utils/functions')


// get all plates
/* 
url: /plates/?page=0&perpage=10
request GET json:
request body can be any query options.
query a plateId: {'plateId':'6125506475'}
return json list of plates.
[{
'_id': '5fc47ad71ea7ca9d7d0d03ea',
'plateId': '6125506475',
'step': 'lyse',
'layout': ,
'wells':{},
'created':'2020-11-30T04:53:43.948Z',
'companion': '1234567890',
'meta':{},
'result':{},
},...]
*/
router.get('/',(req,res)=>{
    let page = parseInt(req.query.page) || 0
    let perpage = parseInt(req.query.perpage) || 10
    Plate.find(req.body,null,{lean:true,})
    .sort({created:-1})
    .limit(perpage)
    .skip(page*perpage)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})

// get One plate by plateId
/* 
url: /plates/id/1234567890
requset GET
return json document.
{
 fileds of a plate.
}
*/
router.get('/id/:plateId',(req,res)=>{
    Plate.findOne({plateId:req.params.plateId},)
    .then((doc) =>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})


// add one plate to database
/* 
url: /plates
request POST json
{
    plateId: 1234567890,
    step: 'lyse' or 'lamp',
    layout: 
    companion: used at the lamp step and using separate plate for N7 and RP4.
    wells:{A1:{sampleId:1234567890,
              type:ukn-N7, ukn-RP4, ntc-N7, ntc-RP4, ptc-N7, ptc-RP4,iab-N7,iab-RP4
              raw: reading result
            } ...}
}
return json:
the plate document created.
*/
router.post('/',(req,res)=>{     
    Plate(req.body).save()
    .then(docs=>{
        res.json(docs)
    })
    .catch(err=>ErrorHandler(err,res))
})
 
//update plate field.
/* 
url: /plates
request PUT json:
{
    plateId: id to identify the plate.
    step: 'lamp',
    wells: {A1:{raw:1234}...} # to update raw reading result
    other fileds is set.
}
response json:
the updated plate document.
*/
router.put('/',(req,res)=>{         
    let update = {};
    let plateId = req.body.plateId;
    // assemble the update    
    for (let field in req.body) {
        if (field=='wells') {
            for (let well in req.body.wells) {
                for (let prop in req.body.wells[well]) {
                    update[`wells.${well}.${prop}`] = req.body.wells[well][prop]
                }
            }
        } else {
            update[field] = req.body[field]
        }
    }
    Plate.findOneAndUpdate({plateId},{$set:update},{new:true,lean:true})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

// used to link a new plate to old plate.
/* 
url: /plates/link
request PUT json:
{
    oldId: old plate Id
    newId: new plate Id
    step: current step name.
    companion: 1234567890
}
response json:
updated plate document, without wells.
*/
router.put('/link',(req,res)=>{
    let plateId = req.body.oldId;
    let update = {...req.body}
    delete update.oldId
    delete update.newId
    update.plateId = req.body.newId
    Plate.findOneAndUpdate({plateId},
        {$set:update},
        {new:true,lean:true,projection:{__v:0,_id:0,}})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

// delete a plate
router.delete('/',(req,res)=>{
    Plate.findOneAndDelete({sampleId:req.body.sampleId},{projection:'-wells'})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})

module.exports = router