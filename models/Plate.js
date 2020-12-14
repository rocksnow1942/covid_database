const mongoose = require('mongoose')


const Plate = mongoose.Schema({
    plateId:{
        type:String,
        trim:true,
        required:[true,'Plate Id required.'],
        unique:[true,'Plate Id duplicate found.'],
        index:true,
    },
    // step is the Step name of the plate
    step:{
        type:String,
        enum:['lyse','lamp',],
        required:[true,'Step name required,(lyse or lamp)']
    },
    // name of plate layout.
    layout:{
        type:String,         
        required: [true,'layout name required.']
    },
    companion:{
        type:String,
        trim:true,  
    },
    created:{
        type:Date,
        default:Date.now
    },
    //meta store other information, for example, the method about plate reading.
    meta:{}, 
    //result store some analysis result, like IAB avg, cv etc...
    result:{},
    // wells store the information about individual well.
    // format should be: {A1: {sampleId, type, raw}}
    wells: {}    
})

module.exports = mongoose.model('Plate',Plate,'plate')