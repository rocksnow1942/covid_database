
//middleware that attach the user name to req.
module.exports.Auth = (req, res, next) => {
    // the auth method attach user property to request. 
    if (req.headers.authorization) {
        req.user = JSON.parse(req.headers.authorization)        
    } else {
        req.user = {username:'admin'}
    }
    return next()
  };