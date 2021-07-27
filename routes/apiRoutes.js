const router = require('express').Router();
const path = require('path');
const fs = require('fs');
const multer  = require('multer');

const upload = multer({ dest: 'firmware/',
 })

const FIRMWARE_FOLDER = path.join(process.cwd(), 'firmware');

/*
download a particular verison of a firmware
*/
router.get('/aceFirmware/:version',(req, res) => {
    let version = req.params.version;
    res.setHeader('content-type','application/x-tar');
    let file = path.join(FIRMWARE_FOLDER, version)

    fs.stat(file, (err, stats) => {
        if (err) {
            res.status(404).send(err);
        }
         else { 
             if (stats.isFile()) {
                fs.createReadStream(file).pipe(res);
             } else {
                 res.status(400).send('Not valid file.');
             }            
         }
    })    
})

/*
get a list of all available firmware versions
*/
router.get('/availableFirmware', (req, res) => {
   fs.readdir(FIRMWARE_FOLDER, (err, files) => {
       if (err) {
           res.status(404).send(err);
       }
       else {
           res.json(files);
       }
   })
})

/*
upload firmware and save file in firmware folder
*/
router.post('/aceFirmware', upload.single('file'), (req, res) => {
    const tmpPath = req.file.path;
    const targetPath = path.join(FIRMWARE_FOLDER, req.file.originalname);
    fs.rename(tmpPath, targetPath, (err) => {
        if (err) {
            res.status(400).send(err);
        }
        else {
            res.status(200).send('File uploaded successfully');
        }
    })

})




module.exports = router;