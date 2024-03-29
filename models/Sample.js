const mongoose = require('mongoose')

// subschema for results
const Result = mongoose.Schema({
    result: String, // can be positive, negative or invalid:RP4(reason)
    plateId:[String],
    testStart:Date,    
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
        // this is when sample doc is created in our database.
        // this is whenever the sample got created in our database. 
        type: Date,
        default: Date.now,
        index:true
    },
    receivedAt: {
        // this  date is our receivedAt date in firebase details
        // for individual client, this date is the same as created and collected.
        // for corporate client, this date is when we first scan the ID on lysis plate.
        type: Date,
        default: Date.now
    },
    collected: { 
        // the date for sample collection, for corporate client, this date is in the submission form. 
        // for individual clients, this information is updated after patient checkin.
        type: Date,
        default: Date.now
    },
    type: {
        type:String,
        default:'saliva'
    },
    //which result in results array to upload, default -1 means determine automatically by default. 
    uploadIdx:{type:Number,default:-1},
    // result have a comment field
    results: [
        Result
    ],
    
    //document id for easy identify document in cloud. Not confused with real external ID in patients.
    extId:{type:String,trim:true,index:true,sparse:true,unique:true},
    
    //ID for the batch if this sample is in a batch /Group_ACCESSION_LOG/VL7Q3lOeFw6dEF8XlJVR
    batchId:{type:String,trim:true,index:true},

    // whether this sample have been reported to cloud. 
    reported:{type:Boolean,default:false},

    // meta stores other information about the sample,
    // e.g. patient ID (this might be necessary for future.), time collected, patient symptoms, etc.
    // the time sample collected will be in created for drive through patients.
    // may be useful to have technician comment on samples and add in meta field. 
    // may have a comment field in meta.    
    // from field: if the field is 'appCreated' means the sample is created by download from firebase by app or by sample accession page.
    // receptionBatchId: batchID in our batch collection, reflect what is this batch of samples. 
    meta: {},
},)

// update all field of a document from an object
Sample.method('updateFields',function(obj){
    for (let k in obj) {
        this[k] = obj[k]
    }
})

module.exports = mongoose.model('Sample',Sample,'sample')