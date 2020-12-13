const mongoose = require('mongoose')

const Store = new mongoose.Schema({
    plateId:{
        type:String,
        trim:true,
        index:true,
        default:"",
    },
    location:{
        type:String,
        trim:true,
        required:[true,'location is requried'],
        unique:[true,'duplicate location found.'],
        index:true
    },
    order:{ //the order of the locations, internally increasing.
        type:Number,
        required:true,
        unique:true,
        default:0
    },
    created:{
        type:Date,
        default:Date.now
    }
})



Store.method('removePlate',function(){
    this.plateId = ""
    this.created = Date.now()
    return this.save()
})

Store.method('putPlate',function(plateId){
    this.plateId = plateId
    this.created = Date.now()
    return this.save()
})




module.exports = mongoose.model('Store',Store,'store')
