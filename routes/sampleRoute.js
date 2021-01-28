const router = require("express").Router();
const Sample = require("../models/Sample");
const { ErrorHandler } = require("../utils/functions");
const dayjs = require("dayjs");
const { Auth } = require("../utils/auth");

// get all samples that match request filter.
/* 
url: /samples/?page=0&perpage=1000
request GET json
query dates: {"created":{"$lt":"2020-11-28T20:21:04.310Z"}}
query results: 
{"results":{"$elemMatch": {"diagnose":"positive"}}}
{"results":{"$elemMatch": {"diagnose":"positive"}}}
{"results.testOn":"123456"}
query a field: {"sampleId":"1234567890"}
query id in a list {'sampleId':{'$in':[id1,id2...]}}
response:
[{'_id': '5fc575b01476bc4d78a8e15d',
  'sampleId': '3183992925',
  'sPlate': '8365473001',
  'sWell': 'G8',
  'created': '2020-11-30T22:44:00.881Z',
  'results': [],
  '__v': 0}]
*/
router.get("/", (req, res) => {
  let page = parseInt(req.query.page) || 0;
  let perpage = parseInt(req.query.perpage) || 1000;
  Sample.find(req.body, null, { lean: true })
    .sort({ created: -1 })
    .limit(perpage)
    .skip(page * perpage)
    .then((docs) => res.json(docs))
    .catch((err) => ErrorHandler(err, res));
});

// add multiple saliva samples to database.
/* 
url: /samples
request POST json:
[{'sampleId': '3050809600',
  'sPlate': '9271107760',
  "created": "date string",
  'sWell': 'C7'},...]
response json:
a list of created documents.
if any sample posted already exist, will return 500
and no sample will be added.
*/
router.post("/", Auth, (req, res) => {
  const handler = req.user.username;
  let samples = req.body.map((doc) => ({
    ...doc,
    created: doc.created ? dayjs(doc.created) : new Date(),
    collected: doc.collected ? dayjs(doc.collected) : new Date(),
    meta:{
      ...doc.meta,
      handler
    }
  }));
  Sample.insertMany(samples)
    .then((docs) => {
      res.json(docs);
    })
    .catch((err) => ErrorHandler(err, res));
});

// update samples with extra information.
/* 
url: /samples
request PUT json:
[{'sampleId': '3050809600',
  'sPlate': '9271107760',
  'sWell': 'C7'},...]
response json:
[
    updated document,
    if Id doesn't exist, return None.
]
*/
router.put("/", async (req, res) => {
  try {
    let results = await Promise.all(
      req.body.map((sample) => {      
        return Sample.findOneAndUpdate(
          { sampleId: sample.sampleId },
          { $set: sample },
          { new: true, lean: true },        
        );
      })
    );
    res.json(results);    
  } catch (err) {
    ErrorHandler(err,res)
  }
});

// update samples with new sampleId
/* 
url: /samples
request PUT json:
{
    sampleId: old sample Id,
    newSampleId : new sample Id
}
response json:
[
    updated document,
    if Id doesn't exist, return None.
]
*/
router.put("/sampleId", async (req, res) => {
  Sample.findOneAndUpdate(
    { sampleId: req.body.sampleId },
    { $set: { sampleId: req.body.newSampleId } },
    { new: true, lean: true }
  )
    .then((doc) => DocOr400(doc, res))
    .catch((err) => ErrorHandler(err, res));
});

// upsert a list of samples to database.
/* 
url: /samples/upsert
request POST json:
a list of documents
response json:
{
    updated:[sampleIds...]
    created:[sampleIds...]
}
*/
router.post("/upsert", async (req, res) => {
  let samples = {};
  let result = {};
  req.body.forEach((s) => (samples[s.sampleId] = s));
  Sample.find({ sampleId: { $in: req.body.map((s) => s.sampleId) } })
    .then((docs) => {
      let updated = [];
      docs.forEach((doc) => {
        updated.push(doc.sampleId);
        doc.updateFields(samples[doc.sampleId]);
        doc.save();
      });
      result.updated = updated;
      return Sample.insertMany(
        req.body.filter((s) => !updated.includes(s.sampleId))
      );
    })
    .then((docs) => {
      result.created = docs.map((doc) => doc.sampleId);
      res.json(result);
    })
    .catch((err) => ErrorHandler(err, res));
});

// delete samples with given sampleId.
/* 
url: /samples
request DELETE json:
[{sampleId:'1234567890'}, ...]
return json:
{'n': 10570, 'ok': 1, 'deletedCount': 10570}
*/
router.delete("/", (req, res) => {
  let samples = req.body;
  Sample.deleteMany({ sampleId: { $in: samples.map((s) => s.sampleId) } })
    .then((docs) => res.json(docs))
    .catch((err) => ErrorHandler(err, res));
});

// get a specific sample
/* 
url: /samples/id/sampleId
request GET
return json:
{document}
*/
router.get("/id/:sampleId", (req, res) => {
  Sample.findOne({ sampleId: req.params.sampleId })
    .then((docs) => {
      if (docs) {
        res.json(docs);
      } else {
        res.status(400).json(docs);
      }
    })
    .catch((err) => ErrorHandler(err, res));
});

//append new results to sample.
/* 
url: /samples/results
request POST json:
[{
    sampleId: ID is used to match the result.
    results: [{
        result:positive,
        plateId:[plateIds, 1234567890,],        
    },...] An array of results. 
}...]
response json:
[
    {updated document},...
]
*/
router.post("/results", async (req, res) => {
  try {
    // Don't use call back here as it will casue the query to execute twice.
    // (err,doc)=>{
    // if (err){
    //     results.push(err)
    // } else {
    //     results.push(doc)
    // }}
    let results = await Promise.all(
      req.body.map((sample) => {
        return Sample.findOneAndUpdate(
          { sampleId: sample.sampleId },
          { $push: { results: { $each: sample.results } } },
          { new: true, lean: true }
        );
      })
    );
    res.json(results);
  } catch (err) {
    ErrorHandler(err, res);
  }
});

module.exports = router;
