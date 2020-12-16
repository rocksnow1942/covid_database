const router = require('express').Router()
const Meta = require('../models/Meta')
const {DocOr400,ErrorHandler} = require('../utils/functions')


// barcode generator route. generate a 10 digit barcode.
/* 
url: /barcode/?type=1&count=99
type can be 0 - 9.
count can be 1-9999
request GET:
response json:
a list of barcodes
maximum count is capped at 9999.
*/
router.get('/barcode',(req,res)=>{
    let count = parseInt( req.query.count)
    let type = parseInt(req.query.type)
    if (!count || !type || count>9999) {
        return res.status(500).json({error:`/meta/barcde/?type=${type}&count=${count} invalid. type is 0-9, count is 1-9999 `})
    }
    let codes = [];
    Meta.findOne({metaType:'barcodeSeed'})
    .then(doc=>{        
        let current = doc.meta[type]
        let num,sum;
        while(count>0){    
            // recycle to 0 if overflow.
            if (current>9999999) {current=0}; 
            num = String(current).padStart(7,'0');
            sum = String(num.split('').reduce((a,b)=>+a+(+b),0)).padStart(2,'0')
            codes.push(type+sum+num)
            count -= 1
            current +=1
        }
        doc.meta[type] = current
        doc.created = Date.now()
        doc.markModified('meta')
        return doc.save()
    })
    .then(doc=>{
        res.json(codes)
    })
    .catch(err=>ErrorHandler(err,res))
})

module.exports = router