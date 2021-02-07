const mongoose = require('mongoose')


// schema for Order data. 
const Batch = new mongoose.Schema({
    batchId:{ // the accesion log docID, /collectionName/documentID
        type:String,
        trim:true,
        required:[true,'batch ID requried'],
        unique:true,
        index:true
    }, // order number. can be used externally
    
    createdAt:{type:Date,default:Date.now}, // batch create time,
    
    sampleCount: Number, //number of samples submitted

    receivedCount:Number, //number of samples received,
   
    note:String, // user note or file name
  
    meta: {},// orther information
},)
 

module.exports = mongoose.model('Batch',Batch,'batch')