const mongoose = require('mongoose')

const Patient = new mongoose.Schema({
    name:{
        type:String,
        trim:true,
        index:true
    },
    dob:{
        type:Date,
    },
    email:{
        type:String,
        index:true
    },
    tel:String,
    age:{
        type:Number
    },
    gender:{
        type:String,
        enum:['male','female','other'],
    },
    address:{
        type:String,
        index:true
    },
    company:{
        type:String,
    },
    // external ID
    extId:{
        type:String, 
        index:true,
    },
    created:{
        type:Date,
        default:Date.now
    },
    other:{}
})

module.exports = mongoose.model('Patient',Patient,'patient')