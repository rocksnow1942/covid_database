const mongoose = require('mongoose')

// subschema for results
const Result = mongoose.Schema({
    result: String, // can be positive, negative or invalid:RP4(reason)
    plateId:[String],
    testStart:Date,    
    comment: String,
    N7: Number,
    N7_NTC:Number,
    N7_PTC:Number,
    N7_NTC_CV:Number,
    N7_PTC_CV:Number,
    N7_NBC_CV:Number,
    RP4: Number,
    RP4_NTC:Number,
    RP4_PTC:Number,
    RP4_NTC_CV:Number,
    RP4_PTC_CV:Number,
    RP4_NBC_CV:Number,
    testEnd:{
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
    type: {
        type:String,
        default:'saliva'
    },

    // result have a comment field
    results: [
        Result
    ],

    
    //document id for easy identify document in cloud. Not confused with real external ID in patients.
    extId:{type:String,trim:true},
    
    // document ID in the firebase cloud diagnose collection. this value is returned after save the result to cloud.
    diagnoseId:{type:String,trim:true},

    // whether this sample have been reported to cloud. 
    reported:{type:Boolean,default:false},

    // meta stores other information about the sample,
    // e.g. patient ID (this might be necessary for future.), time collected, patient symptoms, etc.
    // the time sample collected will be in created for drive through patients.
    // may be useful to have technician comment on samples and add in meta field. 
    // may have a comment field in meta.
    meta: {},
},)

// update all field of a document from an object
Sample.method('updateFields',function(obj){
    for (let k in obj) {
        this[k] = obj[k]
    }
})

module.exports = mongoose.model('Sample',Sample,'sample')