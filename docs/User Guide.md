# Thoughts On Lab Testing Setup

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

***TODOs***  
_We can have a website for sample submission._

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
Lyse the sample @95 for 5min.

### Lysed sample to LAMP plate

2 plates are used for 1 sample plate. 1 plate is for N7 primer and the other plate is for RP4 primer.  
N7 and RP4 plates are both preloaded with lamp master mix and IAB NTC on the proper control positions.   

N7 and RP4 plates should be color-coded and barcode labeled. Operator will scan the lysed sample plate barcode first. Then scan the LAMP-N7 plate and then the LAMP-RP4 plate. 

The scaned barcodes are validated against database. Valid results is then saved to database.

Perform LAMP reaction for 30minutes on thermal cycler.

### Read LAMP results

Completed LAMP reaction plate is read on qPCR. The result is exported and saved to a dedicated folder.

The barcode on the plate is read through a barcode sanner and used to name the file during running. The exported csv file is saved to a folder and synced to cloud station. A file monitor will monitor the creation of new exported result and process and save result to database.


## Appendix

#### Layout Well Type encoding
The following single letter is used to mark each kind of samples on the plate in database.
>```
>    # layoutmap encoding:
>    # N-> ukn-N7, R-> ukn-RP4,
>    # O-> N7 NTC, S-> RP4 NTC,
>    # P-> N7 PTC, T-> RP4 PTC,
>    # Q-> N7 IAB, U-> RP4 IAB
>```

#### Currently supported layout types
**Sample88_2NTC_3PTC_3IAB layout**
```
              1  2  3  4  5  6  7  8  9 10 11 12
    ROW   A   N  N  N  N  N  N  N  N  N  N  N  O
    ROW   B   N  N  N  N  N  N  N  N  N  N  N  O
    ROW   C   N  N  N  N  N  N  N  N  N  N  N  P
    ROW   D   N  N  N  N  N  N  N  N  N  N  N  P
    ROW   E   N  N  N  N  N  N  N  N  N  N  N  P
    ROW   F   N  N  N  N  N  N  N  N  N  N  N  Q
    ROW   G   N  N  N  N  N  N  N  N  N  N  N  Q
    ROW   H   N  N  N  N  N  N  N  N  N  N  N  Q
```
**VariableSample_2NTC_3PTC_3IAB**  
Same control sample layout as above, however can have any number of uknown samples.

#### Barcode Requirements

The sample collection tube barcode is from vendor and we cannot control its format.

All our internal barcodes will be 10 digit numeric barcodes. The first digit is used to indicate the type of the plate.
The second and third digit of the barcode is used to generate check sum validator. 
The last 7 digits are used as unique ID.
The entire 10 digits is stored in the database.

- **Sample storage rack barcode**  
    >Sample storage rack barcode should start with 0 or 1. 
    >Currently, Useing 0 to indiate a full plate and use 1 to indiate variable sample count plate.

- **Lyse plate barcode**
    >Lyse plate barcode should start with 2.

- **LAMP-N7 plate barcode**
    >LAMP-N7 plate barcode should start with 3.
- **LAMP-RP4 plate barcode**
    >LAMP-RP4 plate barcode should start with 4.

    