const router = require('express').Router()
const Sample = require('../models/Sample')
const {ErrorHandler} = require('../utils/functions')

// logging all request middleware
// router.use((req,res,next)=>{
//     const current = new Date().toLocaleString()
//     logger.debug('Time: '+ current +' Received in sample Test route.')
//     next()
// })


// get all samples that match request filter.
/* 
get: /samples/?page=0&perpage=1
query dates: "created":{"$lt":"2020-11-28T20:21:04.310Z"}
query results: 
"results":{"$elemMatch": {"diagnose":"positive"}}
"results":{"$elemMatch": {"diagnose":"positive"}}
"results.testOn":"123456"
query a field: {"sampleId":"1234567890"}
*/
router.get('/',(req,res)=>{
    let page = parseInt(req.query.page) || 0
    let perpage = parseInt(req.query.perpage) || 1000
    Sample.find(req.body,null,{lean:true})
    .sort({created:-1})
    .limit(perpage)
    .skip(page*perpage)
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})


// add multiple saliva samples from a plate to database.
/* 
    data is a list of samples,
    each sample should include: {
        sampleId: 10 digit ID,
        patientId(optional):  ID used for patients.
        sPlate: sample plate ID the sample is on.
        sWell: the well the sample is in.
    }
*/
router.post('/',(req,res)=>{
    let samples = req.body;
    Sample.insertMany(samples)
    .then(docs=>{
        res.json(docs)
    })
    .catch(err=>ErrorHandler(err,res))

})

// update samples with relative information. 
/* 
    data is a list of samples,
    the sampleId of each sample is used to find data,
    then each field is used to set the respective field in database.
*/
router.put('/',async (req,res)=>{
    let results = []
    await Promise.all(req.body.map(async (sample)=>{
        let sampleId = sample.sampleId;
        await Sample.findOneAndUpdate({sampleId},{$set:sample}, 
            {new:true,lean:true},
            (err,doc)=>{            
            if (err){
                results.push(err)
            } else {
                results.push(doc)
            }            
        })
    }))    
    res.json(results)    
})

// upsert samples, similar to put('/')
// router.post('/upsert',async (req,res)=>{
//     let results = []
//     await Promise.all(req.body.map(async (sample)=>{
//         let sampleId = sample.sampleId;
//         await Sample.findOneAndUpdate({sampleId},{$set:sample}, 
//             {new:true,lean:true,upsert:true},
//             (err,doc)=>{            
//             if (err){
//                 results.push(err)
//             } else {
//                 results.push(doc)
//             }            
//         })
//     }))    
//     res.json(results)    
// })

// upsert version 2 similar to version 1,a lot faster.
router.post('/upsert',async (req,res)=>{
    let samples = {}
    let result = {}
    req.body.forEach(s=>samples[s.sampleId]=s)
    Sample.find({sampleId:{$in:req.body.map(s=>s.sampleId)}})
    .then(docs=>{
        let updated = []
        docs.forEach(doc=>{
            updated.push(doc.sampleId)
            doc.updateFields(samples[doc.sampleId]);
            doc.save()
        })
        result.updated = updated
        return Sample.insertMany(req.body.filter(s=>!updated.includes(s.sampleId)))
    })
    .then(docs=>{
        result.created = docs.map(doc=>doc.sampleId)
        res.json(result)
    })
    .catch(err=>ErrorHandler(err,res))    
})


// delete samples with given sampleId.
/* 
    request data is a list of samples.
    each sample Id is used to find and delete the sample data.
*/
router.delete('/', (req,res)=>{  
    let samples = req.body
    Sample.deleteMany({sampleId:{$in:samples.map(s=>s.sampleId)}})
    .then(docs=>res.json(docs))
    .catch(err=>ErrorHandler(err,res))
})



// get a specific sample
/* 
request url: /samples/id/sampleId
return the document for the sampleId. 
*/
router.get('/id/:sampleId',(req,res)=>{
    Sample.findOne({sampleId:req.params.sampleId},)
    .then((docs) => {
        if (docs){
            res.json(docs)
        } else {res.status(400).json(docs)}
        })
    .catch(err=>ErrorHandler(err,res))
})

//append new results to sample.
/* 
request body is a list of samples
{
    sampleId: ID is used to match the result.
    results: [] An array of results. 
}
*/
router.post('/results',async (req,res)=>{
    let results = []
    await Promise.all(req.body.map(async (sample)=>{
        let sampleId = sample.sampleId;
        await Sample.findOneAndUpdate({sampleId},{$push:{results:{$each:sample.results}}}, 
            {new:true,lean:true},
            (err,doc)=>{            
            if (err){
                results.push(err)
            } else {
                results.push(doc)
            }            
        })
    }))    
    res.json(results)   
})


module.exports = router