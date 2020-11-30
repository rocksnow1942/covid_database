const logger = require('./logger')

function ErrorHandler(err,res) {
    logger.error(err)
    res.status(500).json(err)
}

function DocOr400(doc,res){
    if (doc) {res.json(doc)}
    else {res.status(400).json(doc)}
}

module.exports = {ErrorHandler,DocOr400}