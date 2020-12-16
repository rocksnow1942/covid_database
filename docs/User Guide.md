# Thoughts On Lab Testing Setup
---

## Saliva sample collection tube encoding
The saliva sample tube is encoded with a DataMatrix on the bottom.
DataMatrix is perferred to be 12X12. And the ID is preferred to be 10 numeric digits. However, other format is acceptable.

The collected samples should have the information for saliva sample ID linked to patient ID.
The list of sample IDs is then enterred the database.

The samples are collected on the micronic rack when sent in.

When we receive the samples, we should also receive a sample submission form, with all the sample collection tube IDs.
The collected sample collection tube IDs is used to validate the barcode during our testing process. 

The sample collection tube ID will be uploaded to database. If we have patient ID, the patient ID can also be uploaded together with their associated sample ID.

We can also batch these samples and creat a batch in the database so that we can easily extract all the result of one batch samples to return to client.

## Prepare Saliva sample on storage plate 
The saliva sample collection tube is first neutralized.  

After neutralization, the samples are re-arranged to better fit the plate layout of our workflow.
Assume if we use the **Sample88_2NTC_3PTC_3IAB layout** bellow, we will leave the 12th column on each 96-well rack empty. Extra samples on the rack will be organized and combined to other racks.  

This rack will be used during decapping, transfer saliva sample to lyse plate and storage. 

Control tubes is then added to the rack. This include 3 tubes for PTC and 5 tubes for NTC and IAB NTC.
The PTC samples can be virus spiked in saliva. The NTC and IAB NTC will be water.

## Neutralize saliva sample

Sample on the rack is neutralzied inside an oven or water bath.

## Saliva sample to Lyse plate

Decontaminate the sample tubes and rack. If we use oven, this process might not be necessary as long as we keep the previous step clean.

An internal barcode is used to label the rack. The barcode should suffice requirements in **Barcode Requirements** section. We can print out the barcode. The operator will attach the barcode to the rack. 
The label material should be able to withstand **bleach, 70% alcohol and storage at 4deg**. 

Lyse plate can be color-coded, and a barcode is allready attached to the plate before-hand. The barcode should suffice requirements in **Barcoe Requirements** section. 5ul of lysis buffer is aliquoted to each well.

Operator will scan the barcode on the sample rack first. Then will scan the samples on the rack. These sample IDs will be validated against the known sample IDs in the database. 
The barcode of the lyse plate is then scanned.

Sample is then transferred from the sample rack to the lyse plate.





## Appendix
---

#### Layout Well Type encoding
The following single letter is used to mark each kind of samples on the plate in database.
>```
>   N-> ukn-N7, R-> ukn-RP4,
>   O-> N7 NTC, S-> RP4 NTC,  
>   M-> N7 PTC, Q-> RP4 PTC,  
>   P-> N7 IAB, T-> RP4 IAB
>```

#### Currently supported layout types
**Sample88_2NTC_3PTC_3IAB layout**
```
NNNNNNNNNNNO
NNNNNNNNNNNO
NNNNNNNNNNNP
NNNNNNNNNNNP
NNNNNNNNNNNP
NNNNNNNNNNNQ
NNNNNNNNNNNQ
NNNNNNNNNNNQ
```
**VariableSample_2NTC_3PTC_3IAB**  
Same control sample layout as above, however can have any number of uknown samples.

#### Barcode Requirements


