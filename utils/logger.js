const {format,createLogger,loggers,transports} = require('winston')
const logger = createLogger({
    level:process.env.LOG_LEVEL,
    format:format.combine(
        format.timestamp({
            format:'YYYY-MM-DD HH:mm:ss'
        }),
        format.errors({stack:true}),
        format.splat(),
        format.json()
    ),
    defaultMeta:{ service:'covid-app'},
    transports:[
        new transports.File({filename:process.env.LOG_FILE,})
        // new transports.File({filename:"winston-info.log",level:'error'})
    ]
})

if (process.env.NODE_ENV!=='production') {
    logger.add (new transports.Console({
        foramt:format.combine(
            format.colorize(),
            format.simple()
        )
    }))
}

module.exports = logger