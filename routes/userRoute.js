const router = require('express').Router()
const User = require('../models/User')
const {DocOr400,ErrorHandler} = require('../utils/functions')


/* 
get User by token
Get /user/:token
return user Document
*/
router.get('/:token',(req,res)=>{
    const token= req.params.token    
    User.findOne({token})
    .then(doc=>DocOr400(doc,res))
    .catch(error=>ErrorHandler(error,res))
})



module.exports=router