const mongoose = require('mongoose')


// schema for Order data. 
const Order = new mongoose.Schema({
    orderId:{
        type:String,
        trim:true,
        required:[true,'order ID requried'],
        unique:true,
        index:true
    }, // order number. can be used externally
    patientIds:[{type:String,trim:true}], // a list of patient ID in this batch.
    sampleIds:[{type:String,trim:true}], // a list of sample IDs in this batch.
    created:{type:Date,default:Date.now},
    contact: {
        name: String,
        tel: String,
        email: String,
    }, // contact information
    meta: {},// orther information
},)
 

module.exports = mongoose.model('Order',Order,'order')