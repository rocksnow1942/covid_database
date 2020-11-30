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
    patientId: {
        type: ObjectId,
        trim: true,
        index:true
    },
    sPlate: {
        type:String,
        trim:true,
        required:[true,'sample plate Id required']
    },
    sWell: {
        type: String,
        trim:true,
        required:[true,'sample well required']
    },
    created: {
        type: Date,
        default: Date.now
    },
    results: [
        Result
    ]    
},)

// update all field of a document from an object
Sample.method('updateFields',function(obj){
    for (let k in obj) {
        this[k] = obj[k]
    }
})

module.exports = mongoose.model('Sample',Sample,'sample')