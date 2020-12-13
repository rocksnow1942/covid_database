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
        enum:['96Sample','96Ctrl','48Sample'],
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
    wells: {}    
})

module.exports = mongoose.model('Plate',Plate,'plate')