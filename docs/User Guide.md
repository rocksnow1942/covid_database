# Instructions On Lab Testing Setup
---

## Saliva sample collection tube encoding
The saliva sample tube is encoded with a DataMatrix on the bottom.
DataMatrix is perferred to be 12X12. And the ID is preferred to be 10 numeric digits. However, other format is acceptable.

The collected samples should have the information for saliva sample ID linked to patient ID.
The list of sample IDs is then enterred the database.

The samples are collected on the micronic rack when sent in.

## Prepare Saliva sample on storage plate 
The saliva sample collection tube is first neutralized.  

After neutralization, the samples are re-arranged to better fit the plate layout of our workflow.
Assume if we use the **Sample88_2NTC_3PTC_3IAB layout** bellow, we will leave the 12th column on each 96-well rack empty. Extra samples on the rack will be organized and combined to other racks.  

This rack will be used during decapping, transfer saliva sample to lyse plate and storage. 

An internal barcode is used to label the rack. The barcode should suffice requirements in **Barcode Requirements** section.



## Layout Well Type encoding

>```
>   N-> ukn-N7, R-> ukn-RP4,
>   O-> N7 NTC, S-> RP4 NTC,  
>   M-> N7 PTC, Q-> RP4 PTC,  
>   P-> N7 IAB, T-> RP4 IAB
>```

## Appendix
---
####

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


