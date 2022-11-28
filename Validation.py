import csv




# for counting home and garage
def serv_category():
    with open('services_mock_1.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count=1
        home=0
        garage=0
        for row in csv_reader:
            if row['category'] == 'home':
                home+=1
            elif row['category'] == 'garage':
                garage+=1
        #print(home, garage)
    return home , garage
#for validation of mobile number
def mobileValidation(num): #give number as parameter, this will return 'True' or 'False'
    n = str(num)
    if n.strip().isdigit() and len(n) == 11:
        return True
    else:
        return False

## will check the name | return True or False
def nameCheck(name):
    if name.strip().isalpha():
        return True
    else:
        return False

##
def cnicCheck(cnic):
    n = str(cnic)
    n = n.strip()
    if n.isdigit() and len(n) == 13:
        return True
    else:
        return False


# next Id for parts checker, just give array as parameter then it will return the next id
def nextId(data):
    temp = len(data)
    temp = temp + 1

    count = str(temp)

    if len(count) < 2:
        return "0" + count 
    else:
        return count 