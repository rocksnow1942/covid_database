# In case of Server Down, how do we get the results?

### In this package, I described the procedure and prepared scripts that can be ran mannual to read test reuslts and upload to client.

### The assumption is that we have no server capability in the lab.

1. Patient Accession Need to be done correctly.
    
        This can be done via Pi Scanner or even manually enter tube IDs in CUBE.

2. Place tubes on sample rack for heat - inactivation. 
3. Read the tube IDs using PiScanner - To CSV page. 

        In this step, label the sample rack with a barcode, then read this barcode.
        Then scan the tubes on the rack.
        User need to mannually verify the tubes on the rack are all scaned.
        Then Pi Scanner will save the postion - tube ID link to a txt file.
        The txt file will named as the Plated barcode ID _ time string.

4. In the following steps, user need to mannually keep track of the plate ID on to the reaction plate.
5. In the plate reading step, read the plate with qPCR, enter the previously saved plate ID in qPCR before scan.

        This way, the plate ID is written to the qPCR data file, and will be exported to
        the ID field in csv file exported by bioRad CFX96.


6. Gather the plate position - tube ID txt file, and the raw data export. 


7. In CUBE, pull down all patient records that was checked in today and have test results due. Export 
records to csv file. Necessary headers: ID and sample ID
