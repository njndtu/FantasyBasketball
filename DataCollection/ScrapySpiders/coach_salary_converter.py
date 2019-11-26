import sys
import csv
onemore = True
allem = list()

while(onemore):
    

    number = input("What Number?")
    college = input("What College?")
    conference = input("What Conference?")
    print("Paste raw info and press enter and CTRL-D")
    raw_data = sys.stdin.readlines()


    for entry in raw_data:
        things = entry.split()
        one_new = list()
        one_new.append(number)
        one_new.append(college)
        one_new.append(conference)
        one_new.extend(things)
        allem.append(one_new)
        #print(one_new)

    onemore = bool(input("press enter for no more, 1 for yes more"))

    
print(allem)

file_writer = open('coach_salaries.csv','a')
file_writer = csv.writer(file_writer ,  delimiter='/', quotechar='|', quoting=csv.QUOTE_MINIMAL)
for onerow in allem:
    file_writer.writerow(onerow)
