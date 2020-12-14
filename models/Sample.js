const { ObjectId } = require('mongodb')
const mongoose = require('mongoose')

// subschema for results
const Result = mongoose.Schema({
    diagnose: String,
    testOn:[String],
    desc: String,
    note:String,
    created:{
        type:Date,
        default:Date.now
    }
},{_id:false})

// schema for sample data. 
const Sample = new mongoose.Schema({
    sampleId: {
        type:String,
        trim: true,
        required:[true, 'sample Id required'],
        unique: true,
        index:true
    },
    sPlate: {
        type:String,
        trim:true,
    },
    sWell: {
        type: String,
        trim:true,
    },
    created: {
        type: Date,
        default: Date.now
    },
    results: [
        Result
    ],
    // meta stores other information about the sample,
    // e.g. time collected, patient symptoms, etc.
    meta: {},   
},)

// update all field of a document from an object
Sample.method('updateFields',function(obj){
    for (let k in obj) {
        this[k] = obj[k]
    }
})

module.exports = mongoose.model('Sample',Sample,'sample')