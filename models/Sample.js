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


Sample.method('updateFields',function(doc){
    for (let k in doc) {
        this[k] = doc[k]
    }
})

module.exports = mongoose.model('Sample',Sample,'sample')