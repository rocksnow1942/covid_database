const mongoose = require('mongoose')
const logger = require('./logger')
mongoose.set('useFindAndModify', false)
mongoose.set('useCreateIndex',true)
function connectDB  (URI) {
    try {
        mongoose.connect(
            URI,
            {useNewUrlParser:true,
            useUnifiedTopology:true,
            keepAlive:true,
            keepAliveInitialDelay:300000,
            });
        mongoose.connection.on('error',err=>{
            logger.error(err)
        });
        mongoose.connection.once('open',()=>{
            logger.info(`Connected to ${URI}`)
        })
    } catch (err) {
        logger.error(err)
        process.exit(1)
    }
}

module.exports = connectDB