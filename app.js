require('dotenv/config')
const logger = require('./utils/logger')
const express = require('express')
const app = express()
app.use(express.json({limit:'50mb'}))

const connectDB = require('./utils/db')
connectDB(process.env.DB_URI)


// TODO:
// 1. batch route to store a batch of samples ID
// 2. complete patient route


// pooling route to know if server is alive.
app.get('/',(req,res)=>{
    res.json({live:true})
})

// use routes
const sampleRoute = require('./routes/sampleRoute')
app.use('/samples',sampleRoute)

const plateRoute = require('./routes/plateRoute')
app.use('/plates',plateRoute)

const storeRoute = require('./routes/storeRoute')
app.use('/store',storeRoute)

const patientRoute = require('./routes/patientRoute')
app.use('/patients',patientRoute)

// start app
app.listen(process.env.APP_PORT, ()=>{
    logger.info('started at '+process.env.APP_PORT);
})
