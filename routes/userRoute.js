const router = require('express').Router()
const User = require('../models/User')
const {DocOr400,ErrorHandler,randomString} = require('../utils/functions')


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

/* 
create user
post /user
josn body:{
    username,
    role: [admin,reception,testing],
    email,dob,phone
}
*/
router.post('/',(req,res)=>{
    const token = randomString(10)
    User.create({...req.body,token})
    .then(doc=>DocOr400(doc,res))
    .catch(err=>ErrorHandler(err,res))
})


module.exports=router