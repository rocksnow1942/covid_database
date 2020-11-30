require('dotenv/config')
const logger = require('./utils/logger')
const express = require('express')
const app = express()
app.use(express.json({limit:'10mb'}))

const connectDB = require('./utils/db')
connectDB(process.env.DB_URI)




// use routes
const sampleRoute = require('./routes/sampleRoute')
app.use('/samples',sampleRoute)

const plateRoute = require('./routes/plateRoute')
app.use('/plates',plateRoute)

const storeRoute = require('./routes/storeRoute')
app.use('/store',storeRoute)

// start app
app.listen(process.env.APP_PORT, ()=>{
    logger.info('started at '+process.env.APP_PORT);
})

