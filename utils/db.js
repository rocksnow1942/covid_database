const mongoose = require('mongoose')
const logger = require('./logger')

const connectDB = async (URI) => {
    try {
        const conn = await mongoose.connect(
            URI,
            {useNewUrlParser:true,
            useUnifiedTopology:true});
        logger.info('mongodb connected.')
    } catch (err) {
        logger.error(err)
        process.exit(1)
    }

}

module.exports = connectDB