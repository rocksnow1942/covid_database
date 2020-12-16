const mongoose = require('mongoose')


// schema for store of meta information. 
const Meta = new mongoose.Schema({
    metaType:String,
    meta:{},
    created:{type:Date,default:Date.now},
    desc:String,
},)
 

module.exports = mongoose.model('Meta',Meta,'meta')