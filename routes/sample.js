const express = require('express')
const router = express.Router()
const SampleTest = require('../models/SampleTest')
const logger = require('../utils/logger')

router.use((req,res,next)=>{
    const current = new Date().toLocaleString()
    logger.debug('Time: '+ current +' Received in sample Test route.')
    next()
})

router.get('/',(req,res)=>{
    console.log(req.params.sampleId);
    console.log(req.body)
    SampleTest.find((err,docs)=>{
        res.json(docs)
    })
})


router.get('/:sampleId',(req,res)=>{
    console.log(req.params.sampleId);
    SampleTest.find({sampleId:req.params.sampleId},(err,docs)=>{
        res.json(docs)
    })
})





module.exports = router