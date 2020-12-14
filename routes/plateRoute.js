const router = require('express').Router()
const Plate = require('../models/Plate')

const {DocOr400,ErrorHandler} = require('../utils/functions')


// get all plates
/* 
query url is used to paginate the result.
request body can be any query options.
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
router.get('/id/:plateId',(req,res)=>{
    Plate.findOne({plateId:req.params.plateId},)
    .then((doc) =>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})


// add one plate to database
/* 
url: /plates
request POST json
[{
    plateId: 1234567890,
    step: 'lyse' or 'lamp',
    layout: 
    companion: used at the lamp step and using separate plate for N7 and RP4.
    wells:{A1:{sampleId:1234567890,
              type:ukn-N7, ukn-RP4, ntc-N7, ntc-RP4, ptc-N7, ptc-RP4,iab-N7,iab-RP4
              raw: reading result
            } ...}
}]
return json:

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
Can only update one plate per request.
{
    plateId: id to identify the plate.
    wells: {A1:{raw:1234}...}
}
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
request body format:
{
    oldId: old plate Id
    newId: new plate Id
    step: current step name.
}
*/
router.put('/link',(req,res)=>{
    let plateId = req.body.oldId;
    Plate.findOneAndUpdate({plateId},
        {$set:{plateId:req.body.newId,step:req.body.step}},
        {new:true,lean:true,projection:'-wells'})
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