# I will write to DK_entries/classic/entered/DKEntries.csv

# Entry ID,Contest Name,Contest ID,Entry Fee are the new things
# ATM, I will need to feed the editor a created csv lineup, that matches up.

# the editor is used for two main reasons, updating entries before tip off, and late swaps.
# if correct, player's are locked in when tip off occurs for their respected games
# complete overwrite with another csv file, or replacement.

# current goals should be to improve the 150(0.50) + 20(0.25) games
# I essentially wanna place 170 unique lineups, 0.25 or 0.50 dont matter
# the number of lineups in both csv files should be thr same

# I may run into uncertainties with injuries, hence I need to precompute the "different" scenarios ahead of time. Editor needs to be able to replace all 170 with different scenarios depending on that day. (NEED to test the speed of draftkings updating)

#



import csv 

name = str(input("Which CSV file to use, no need to include .csv . . . . . "))
orig = open('DK_entries/classic/entered/DKEntries.csv','r')
reader_orig = csv.DictReader(orig)


new_one = open('DK_entries/classic/entered/DKEntriesToUse.csv','w')
fieldnames = ['Entry ID','Contest Name','Contest ID','Entry Fee','PG','SG','SF','PF','C','G','F','UTIL']

writer = csv.DictWriter(new_one,fieldnames=fieldnames)
writer.writeheader()

ref = open('DK_entries/classic/created/'+name+'.csv','r')
reader_ref = csv.DictReader(ref)

game_sets = list()


    


for row,row2 in zip(reader_ref,reader_orig):
    writer.writerow({'Entry ID':row2['Entry ID'],'Contest Name':row2['Contest Name'],'Contest ID':row2['Contest ID'],'Entry Fee':row2['Entry Fee'],'PG':row['PG'],'SG':row['SG'],'SF':row['SF'],'PF':row['PF'],'C':row['C'],'G':row['G'],'F':row['F'],'UTIL':row['UTIL']})


#for row in reader_orig:
 #   writer.writerow({'Entry ID':row['Entry ID'],'Contest Name':row['Contest Name'],'Contest ID':row['Contest ID'],'Entry Fee':row['Entry Fee']})
