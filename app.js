require('dotenv/config')
const logger = require('./utils/logger')
const express = require('express')
const app = express()

const connectDB = require('./utils/db')
connectDB(process.env.DB_URI)

const bodyParser = require('body-parser')
const sampleTestRoutes = require('./routes/sample')

app.use(bodyParser.json())


// use routes
app.use('/sample',sampleTestRoutes)


// start app
app.listen(process.env.APP_PORT, ()=>{
    logger.info('started at '+process.env.APP_PORT);
})

