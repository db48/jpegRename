#this program will read in a .csv and use it to copy files and rename them


import csv
from os import listdir
from os.path import isfile, join
from shutil import copyfile


#some control parameters
inputPath = '../../renameTheseFiles/'
outputPath = '../../renamedFiles/'
csvFile = '../../C_Skus_1.csv'
errorFile = '../../renamedFiles/errors.txt'
skuColNum = 8
spineColNum = 4

fp = open(errorFile,'w') 

fp.write('-------------------EXCEL FILE ANALYSIS------------------------\n')

#first let's import the mapping between spine and sku
with open(csvFile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    entry_count = 0
    dvd_count = 0
    spine = []
    sku = []
    title = []

    for row in csv_reader:
        if ( 'BLU' in row[0] ):
            #this is where we'll read the columns we want
            for sn in row[spineColNum].split(','):
                for sn2 in sn.split('/'):
                    if '-' in sn2:
                        sted = sn2.split('-')
                        if len(sted) == 2:
                            for sn_rng in range(int(sted[0]),int(sted[1])):
                                spine.append(int(sn_rng))
                                sku.append(int(row[skuColNum]))
                                title.append(row[1])
                                entry_count += 1
                        else:
                            print(f'Weve got a weird one {sn2}')   
                            fp.write(f'Weve got a weird spine number: {sn2} (raw row:  {", ".join(row)} )\n')                   
                    else:
                        sn3 = sn2.strip()
                        if sn3.isdigit():
                            spine.append(int(sn3))
                            sku.append(int(row[skuColNum]))
                            title.append(row[1])
                            entry_count += 1
                        else:
                            fp.write(f'non integer spine number: {sn2} (raw row:  {", ".join(row)} )\n') 
        elif 'DVD' in row[0] :
            #skip this row because it's a dvd
            dvd_count += 1
        else:
            #skip this line, it's not something I can understand
            #print(f'skipping row with: {", ".join(row)}')
            fp.write(f'skipping row with: {", ".join(row)} \n')
        line_count += 1
    print(f'Processed {line_count} lines, found {entry_count} Bluerays ({dvd_count} dvds).')
    fp.write(f'Processed {line_count} lines, found {entry_count} Bluerays ({dvd_count} dvds).\n')


# find any possible errors and tell us about it
missingSpines = []
badSpines = []
for spID in range(1,851):
    nSpineNums = spine.count(spID)
    if nSpineNums > 1:
        #print(f'problem with spine number {spID}, there are {nSpineNums} occurances in our list')
        badSpines.append(spID)
    if nSpineNums == 0:
        missingSpines.append(spID)
totMissed = len(missingSpines)+len(badSpines)

# now lets get a file list of all of the files in the directory
fileNames = [f for f in listdir(inputPath) if isfile(join(inputPath, f))]

#open the error file for writing
fp.write(f'we are missing a total of {totMissed} spine numbers between 1 and 850 (a total of {850-totMissed}) in the excel file\n')

fp.write('-------------------COVER FILE ANALYSIS------------------------\n')

nFilesMissed = 0
nFiles = 0
nFilesBad = 0
for f in fileNames:
    if '_BD.jpg' in f:
        print(f'.', end='')
        spineIn = f.strip('_BD.jpg')
        for sn in spineIn.split('_'):
            for sn2 in sn.split('-'):
                if sn2.isdigit():
                    if int(sn2) <= 850: #after spine number 850 we don't have to worry about it any more
                        if int(sn2) not in spine:
                            if int(sn2) in missingSpines:
                                #print(f'found cover for {sn2}, but we are missing it from the file')
                                fp.write(f'found cover for {sn2} ({f}), but we are missing it from the file\n') 
                                nFilesMissed += 1
                            else:
                                fp.write(f'found cover for {sn2} ({f}), but we are missing it from the file (error case)\n') 
                                print(f'-------ERROR:spine: {sn2} not found--------')
                                nFilesMissed += 1
                        elif int(sn2) in badSpines:
                            #print(f'skipping {sn2} because there are multiples')
                            fp.write(f'skipping {sn2} ({f}) because there are multiples\n') 
                            xx=2
                        else:
                            spIdx = spine.index(int(sn2))
                            skuOut = sku[spIdx]
                            inputFileName = inputPath+f
                            outputFileName = outputPath+str(skuOut)+'.Main.jpg'
                            if isfile(outputFileName):
                                fp.write(f'!!! not overwriting {outputFileName} with source {inputFileName} ({sn2})\n')
                            else:
                                fp.write(f'writing {outputFileName} with source {inputFileName} ({sn2})\n')
                                nFiles += 1
                            #print(f'spine: {sn2} maps to sku: {skuOut} at index: {spIdx}')
                            #### here is where we'll do the actual renaming!
                            copyfile(inputFileName, outputFileName)
                    else:
                          fp.write(f'not coppying {sn2} ({spineIn}) beacuse it is over 850\n')    
                else:
                    #print(f'spine: {sn2} bad')
                    fp.write(f'skip {sn2} ({f}), because I assume it is not an actual cover\n') 
                    nFilesBad += 1


print(f'there are {nFiles} files to be renamed, and we missed {nFilesMissed}, with {nFilesBad} skipped')
fp.write(f'there were {nFiles} files renamed, and we missed {nFilesMissed}, with {nFilesBad} skipped (all noted above)\n')
fp.close() 

