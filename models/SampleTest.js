const mongoose = require('mongoose')


const SampleTestSchema = new mongoose.Schema({
    sampleId: {
        type:String,
        trim: true,
        required:[true, 'sample Id required']
    },
    patientId: {
        type: String,
        trim: true,
        required:[true,'patientId required']
    },
    sPlate: {
        type:String,
        trim:true,
        required:[true,'sample plate Id required']
    },
    sWell: {
        type: String,
        trim:true,
        required:[true,'sample well required']
    },
    created: {
        type: Date,
        default: Date.now
    },
    results: [
        {
            diagnose: String,
            dataSource:[String],
            summary: String
        }
    ]
    
})


module.exports = mongoose.model('SampleTest',SampleTestSchema,'sampleTest')