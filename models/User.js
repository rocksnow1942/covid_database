const mongoose = require('mongoose')


// schema for internal user
const User = new mongoose.Schema({
    username:{
        type:String,
        trim:true,
        index:true
    },
    role: [String], // a list of roles
    /* roles:
        admin,
        reception,
        testing,
    */
    token:{ // a unique string for user identification
        type:String,
        trim:true,
        index:true,
        unique:true
    },
    email:String,
    dob:String,
    phone:String
},)
 

module.exports = mongoose.model('User',User,'user')