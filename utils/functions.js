const logger = require('./logger')

module.exports.ErrorHandler = (err,res) => {
    logger.error(err)
    res.status(500).json(err)
    return null
}

module.exports.DocOr400 = (doc,res)=>{
    if (doc) {res.json(doc)}
    else {res.status(400).json(doc)}
    return null
}

 


module.exports.randomString =(length)=> {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
       result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
 }