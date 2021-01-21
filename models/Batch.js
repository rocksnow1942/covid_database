const mongoose = require('mongoose')


// schema for Order data. 
const Batch = new mongoose.Schema({
    docID:{ // the accesion log docID, /collectionName/documentID
        type:String,
        trim:true,
        required:[true,'order ID requried'],
        unique:true,
        index:true
    }, // order number. can be used externally
    patientIds:[{type:String,trim:true}], // a list of patient ID in this batch.
    sampleIds:[{type:String,trim:true}], // a list of sample IDs in this batch.
    
    createdAt:{type:Date,default:Date.now}, // batch create time,
    sampleCount: Number, //number of samples submitted
    receivedCount:Number, //number of samples received,
    received:Boolean, // whether this batch is received,
    tested:Boolean, // whether test is done,
    downloaded:Boolean, // whether user downloaded data,
    note:String, // user note or file name
    contact: {
        name: String,
        tel: String,
        email: String,
    }, // contact information
    // meta  contain fields after reception.
    // sampleIds missing, sampleIds received, sample Ids unsatisfactory, sampleIds aberrant, 
    meta: {},// orther information
},)
 

module.exports = mongoose.model('Batch',Batch,'batch')