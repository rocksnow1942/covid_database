const mongoose = require('mongoose')

const stepNames = ['lyse','lamp','read']

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
        enum:stepNames,
        required:[true,`Step name required: ${stepNames.join(',')}`]
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
    history: [ // the time points during linking steps
        {
            step: {type:String,trim:true},
            time: {type:Date,default:Date.now}
        }
    ],
    //meta store other information, for example, the method about plate reading.
    meta:{}, 
    //result store some analysis result, like IAB avg, cv etc...
    result:{},
    // wells store the information about individual well.
    // format should be: {A1: {sampleId, type, raw}}
    wells: {}    
})

module.exports = mongoose.model('Plate',Plate,'plate')