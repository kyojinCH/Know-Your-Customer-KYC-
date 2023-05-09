from itertools import permutations
from difflib import SequenceMatcher
from datetime import datetime
import time
import csv
import numpy as np
import pandas as pd
import json


########################################################### Input files  ######################################################################################
start_time = time.time()

#with open(r"inputListTestV1.csv") as readInput:
#    csvInputReader = csv.reader(readInput)
#    inputList = list(csvInputReader)
    #print(inputList)
    #print("\n")
    
with open(r"inputListTestJson.json") as j:
    inputList = json.load(j)
InputList = ["None",0,0, "None", 0,0,0,0,0]
InputList[1] = inputList["Type"]   
InputList[2] = inputList['Full name']           
InputList[4] = inputList["Nationality"]         
InputList[5] = inputList["Address"]
InputList[6] = inputList["ID card number"]           
InputList[7] = inputList["Birthdate"]
InputList[8] = inputList["Passport Number"]
  

with open(r'watch_list_bis_complète.csv') as readDB:
    csvDBReader = csv.reader(readDB)
    DBList = list(csvDBReader)




############################################################ Other Fs  ######################################################################################

### remaker
## Input : DataBase table formated using the SQL request given in the same file
## Output: Databse formated as : ["ID", "Type", "Name", "Codelist", "Nationalities", "adresses", "ID card number", "Passport", "BirthDate" ]
## Description : This function is simply a parser that rewrite the DB list in an appropriate format for easier computing
def remaker(table: list):       #formatting the DBList to the format I chose
    l = []
    for i in range(len(table)):
        l.append([0,0,[],0,[],[],[],[],[]])
    for i in range(0,len(table)):
        l[i][0] = table[i][0]                       #id
        l[i][1] = table[i][1]                       #type compte
        l[i][2] = table[i][2] + ' '+table[i][3]     #name
        l[i][3] = table[i][5]                       #codeList
        if table[i][6].lower() == 'nationality':
            l[i][4].append(table[i][7])
        if table[i][6].lower() == 'adresse':
            l[i][5].append(table[i][7] + ', ' + table[i][8])
        if table[i][6].lower() == 'piece_identite':
            if table[i][7].lower() == "national identification number":
                l[i][6].append(table[i][8])
            if table[i][7].lower() == "passport":
                l[i][8].append(table[i][8])
        if table[i][6].lower() == 'date_naissance':
            l[i][7].append(table[i][7])
        indice = 0
    while indice < len(l):
        if indice+1 == len(l):
            break
        if l[indice][0] != l[indice+1][0]:
            indice +=1
        elif l[indice][0] == l[indice+1][0]:
            for k in range(4,len(l[0])):
                #if (l[indice][k]== 0 and l[indice+1][k]!=0):
                #if (l[indice][k] == [] and l[indice+1][k] != []):
                if (l[indice][k] != l[indice+1][k] and l[indice+1][k] != []):
                    l[indice][k].append(l[indice+1][k][0])
            l.remove(l[indice+1])
        #if l[indice] == [0,0,0,0,0,0,0,0,0]:
        #   for i in range(indice, len(l)):
        #        l.remove(l[indice])
                       
    return l


### zeroToNone
## Input : the input is the DB list after formating
## Output: return the same lists after removing all 'empty' lines
def zeroToNone(liste : list):
    for i in range(len(liste)):
        for j in range(len(liste[0])):
            if (liste[i][j] == 0 or liste[i][j] == "None" or liste[i][j] == []):
                liste[i][j] = ["none"]
    return liste



### perm
## Input  : the name string
## Output : returns a list with all possible permutations than can be made using the name list
def perm(name: str) -> list:
    finalList = []
    l = name.split(" ")  # mettre chaque mot de la liste dans une case
    finalList = list(permutations(l))  # liste des permutations
    for i in range(len(finalList)):
        finalList[i] = ' '.join(finalList[i])         # joindre chaque tuple de la liste pour former un nom
    return finalList


### compareName
## Input  : finalList        : is the client's name permutation list
##          nameAndAliasList : is the wanted profile's name and alias list 
## Output : returns a list [rate, client's name, highest matching wanted name]
##          the rate is the highest one found
## Description : compare a name with all possibe combinations that can be made with wanted's name and his aliases
### converter
## Input  : a date in string format
## Output : returns that date in EU date format
def compareName(finalList: list, nameAndAliasList: list):
    rate = -1
    finalListOriginal = finalList.copy()
    finalList = list(map(lambda x: x.lower(),finalList ))
    nameAndAliasList = list(map(lambda x: x.lower(),nameAndAliasList ))
    for i in range(len(finalList)):
        for j in range(len(nameAndAliasList)):      
            r = SequenceMatcher(None, finalList[i], nameAndAliasList[j]).ratio()
            if rate < r:
                rate = r  # on choisit le nom avec le plus de similitude
                indexPermList = i
                indexNameAndAliasList = j
                if r == 1:  # si on a similitude parfaite, pas la peine de chercher plus
                    break
    return ([rate, finalListOriginal[indexPermList],  # renvoie le nom avec la plus grande ressemblance, le pourcentage de ressembence
             nameAndAliasList[indexNameAndAliasList]])   # et le nom de la personne


### converter
## Input  : a date in string format
## Output : returns that date in EU date format
def converter(datelist):
    if datelist == "none":
        return 'none'
    format_list=['%d-%m-%Y', '%Y-%m-%d', '%m-%d-%Y', '%Y-%d-%m']
    format_output='%d-%m-%Y'
    #for i in datelist:
     #   datelist[datelist.index(i)] = i.replace("/", "-")
    datelist = list(map(lambda x: x.replace("/", "-"), datelist))
    for date in datelist:
        for date_format in format_list:
            try:
                datelist[datelist.index(date)] =  datetime.strptime(date, date_format).strftime(format_output)
            except ValueError:
                continue      
    return datelist


### compareDate
## Input : birthDate     : is the clients birthdate
##       : birthDateList : is the wanted profile datelist(one profile can have many dates)
## Output: return 0 if there is no match
##       : return 1/(len(birthDateList)) if there is a match
def compareDate(birthDate, birthDateList) -> int:
    birthDate = converter(birthDate)
    birthDateList = converter(birthDateList)
    if birthDateList == "none" or birthDate == "none":
        return 0
    
    birthDate = list(map(lambda x: x.split("-"), birthDate))
    birthDate = list(map(lambda x: datetime(int(x[2]), int(x[1]), int(x[0])), birthDate))
      
    
    b = birthDateList
    b = list(map(lambda x: x.split("-"), b))
    b = list(map(lambda x:  datetime(int(x[2]), int(x[1]), int(x[0])), b)) 
    for i in range(len(b)):
        if b[i] == birthDate[0]:
            #normalement si une date est égale, on renvoie juste 1, mais dans l'éventualité ou on a plusieures dates de naissances
            return 1/len(b)
        else:  # on rajoute cette ligne
            return 0
        
###################################################### Where magic happens ###############################################

### comp
## Description : used to compare binary data(match or not)
def comp(s1, s2):
    if s1 == ['none'] or s2 == ['none']:
        return 0
    for j in range(len(s2)):
        if s1[0].__eq__(s2[j]):
            return 1
    return 0


###resemblanceToData
## Input  : listC  : a list containing the profile's data
##        : listCC : a list containint the wanted profile's data
## Output : a resemblance rate
## Description : The main part is the weight calculation. When a resemblance criteria is not contained in either the 
##               client's data or the wanted profile's data, its weight is distributed evenly between all criteria 
##               which are contained in both profiles.
##               Comparaison is limited to same Type profile. I.e we can only compare individuals to individuals and
##               entities to entities
def resemblanceToData(listC: list, listCC: list):
    weight=[37.9478,37.9478,15.8128,3.79478, 3.45705, 1.03977]
    spareWeight = 1
    if listCC[6].__eq__('ENTITY'):
        weight=[100,0, 0, 0, 0,0]
    for i in range(0,len(listCC)):
            #if (listCC[i].__eq__("none") or listC[i].__eq__("none")):
            if (listCC[i] == ["none"] or listC[i] == ["none"] or listCC[i] == "none" or listC[i] == "none"):
                #for k in range(len(weight)):
                    #if not (listCC[k].__eq__("none") or listC[k].__eq__("none")) :
                        #weight[k] += 1/min([len(listCC)-1 - listCC[0:6].count("none"),len(listC)-1 - listC[0:6].count("none")])*weight[i])
                #weight[i] = 0
                spareWeight += weight[i]
                weight[i] = 0
    for k in range(len(weight)):
        if not(weight[k]==0):
            weight[k] += spareWeight / (len(weight)-weight.count(0))
                        

    
##weight format: [name, nationality, address, id card number, birthdate, passport number]
    resemblance = [0,0,0,0,0,0]
   
    resemblance[0] = compareName(perm(listC[0]), [listCC[0]])[0] * weight[0] # name
    resemblance[1] = comp(listC[1],listCC[1]) * weight[1] # nationality
    resemblance[2] = comp(listC[2] , listCC[2])  * weight[2] # address
    resemblance[3] = comp(listC[3] , listCC[3]) * weight[3] # id card number
    resemblance[4] = compareDate(listC[4], listCC[4]) * weight[4]  # birthdate
    resemblance[5] = comp(listC[5], listCC[5]) * weight[5] # passport number
    
 
    return(sum(resemblance))
    

########################################################### Countries ######################################################################################

# The countries are in english because the used databases are also written in english
countryList = ['afghanistan', 'aland islands', 'albania', 'algeria', 'american samoa', 'andorra', 'angola', 'anguilla', 'antarctica', 'antigua and barbuda', 'argentina', 'armenia', 'aruba', 'australia', 'austria', 'azerbaijan', 'bahamas', 'bahrain', 'bangladesh', 'barbados', 'belarus', 'belgium', 'belize', 'benin', 'bermuda', 'bhutan', 'plurinational state of bolivia', 'bonaire, sint eustatius and saba', 'bosnia and herzegovina', 'botswana', 'bouvet island', 'brazil', 'british indian ocean territory', 'brunei darussalam', 'bulgaria', 'burkina faso', 'burundi', 'cambodia', 'cameroon', 'canada', 'cape verde', 'cayman islands', 'central african republic', 'chad', 'chile', 'china', 'christmas island', 'cocos (keeling) islands', 'colombia', 'comoros', 'congo', 'the democratic republic of the congo', 'cook islands', 'costa rica', "côte d'ivoire", 'croatia', 'cuba', 'curaçao', 'cyprus', 'czech republic', 'denmark', 'djibouti', 'dominica', 'dominican republic', 'ecuador', 'egypt', 'el salvador', 'equatorial guinea', 'eritrea', 'estonia', 'ethiopia', 'falkland islands (malvinas)', 'faroe islands', 'fiji', 'finland', 'france', 'french guiana', 'french polynesia', 'french southern territories', 'gabon', 'gambia', 'georgia', 'germany', 'ghana', 'gibraltar', 'greece', 'greenland', 'grenada', 'guadeloupe', 'guam', 'guatemala', 'guernsey', 'guinea', 'guinea-bissau', 'guyana', 'haiti', 'heard island and mcdonald islands', 'holy see (vatican city state)', 'honduras', 'hong kong', 'hungary', 'iceland', 'indiaindonesia', 'islamic republic of iran', 'iraq', 'ireland', 'isle of man', 'israel', 'italy', 'jamaica', 'japan', 'jersey', 'jordan', 'kazakhstan', 'kenya', 'kiribati', "democratic people's republic of korea", ' republic of kuwait', 'kyrgyzstan', "lao people's democratic republic", 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya', 'liechtenstein', 'lithuania', 'luxembourg', 'macao', 'republic of macedonia', 'madagascar', 'malawi', 'malaysia', 'maldives', 'mali', 'malta', 'marshall islands', 'martinique', 'mauritania', 'mauritius', 'mayotte', 'mexico', 'federated states of micronesia', 'republic of maldova', 'monaco', 'mongolia', 'montenegro', 'montserrat', 'morocco', 'mozambique', 'myanmar', 'namibia', 'nauru', 'nepal', 'netherlands', 'new caledonia', 'new zealand', 'nicaragua', 'niger', 'nigeria', 'niue', 'norfolk island', 'northern mariana islands', 'norway', 'oman', 'pakistan', 'palau', 'occupied palestinian territory', 'panama', 'papua new guinea', 'paraguay', 'peru', 'philippines', 'pitcairn', 'poland', 'portugal', 'puerto rico', 'qatar', 'réunion', 'romania', 'russian federation', 'rwanda', 'saint barthélemy', 'saint helena, ascension and tristan da cunha', 'saint kitts and nevis', 'saint lucia', 'saint martin (french part)', 'saint pierre and miquelon', 'saint vincent and the grenadines', 'samoa', 'san marino', 'sao tome and principe', 'saudi arabia', 'senegal', 'serbia', 'seychelles', 'sierra leone', 'singapore', 'sint maarten (dutch part)', 'slovakia', 'slovenia', 'solomon islands', 'somalia', 'south africa', 'south georgia and the south sandwich islands', 'spain', 'sri lanka', 'sudan', 'suriname', 'south sudan', 'svalbard and jan mayen', 'swaziland', 'sweden', 'switzerland', 'syrian arab republic', 'taiwan, province of china', 'tajikistan', 'united republic of tanzania', 'thailand', 'timor-leste', 'togo', 'tokelau', 'tonga', 'trinidad and tobago', 'tunisia', 'turkey', 'turkmenistan', 'turks and caicos islands', 'tuvalu', 'uganda', 'ukraine', 'united arab emirates', 'united kingdom', 'united states', 'united states minor outlying islands', 'uruguay', 'uzbekistan', 'vanuatu', 'bolivarian republic of venezuela', 'viet nam', 'virgin islands, british', 'virgin islands, u.s.', 'wallis and futuna', 'yemen', 'zambia', 'zimbabwe', 'unknown']


############################################################################## Result ##################################################################################

### csvCompare
## Input  : inputList : is the client's data
##        : DBLits    : is the wanted profile's data
## Output : returns a list of all matching rates, the client's name, the highest matching profile's ID and its name
## Desciprtion : takes the client's data and puts what is needed for the resemblance is a list. Then does the same
##               for each wanted profile. Calls "cvsCompare" and store the rate in a list to be returned in the end.
##               In case you need only the highest matching profile, decomment what is commented, and comment lines 266 
##               to 269
def csvCompare(inputList: list, DBList: list) -> list:
    
    global InputList
    column_set = [
        "rate",
        "wantedID",
        "wantedName"
        ]
    DBList = zeroToNone(remaker(DBList))
    InputList = zeroToNone((InputList))
    rate = [0]*len(inputList)
    #finalList = [0]*len(inputList)
    finalList = []
    index  = [0]*len(inputList)
    listCC = [0,0,0,0,0,0,0]
    listC  = [0,0,0,0,0,0,0]
    for j in range(len(DBList)):
            
        listC[0] = InputList[2] #name
        listC[1] = ["".join(list(map(lambda x: x.lower(),InputList[4])))] # nationality
        listC[2] = ["".join(list(map(lambda x: x.lower(),InputList[5])))] # address
        listC[3] = ["".join(list(map(lambda x: x.lower(),InputList[6])))] # id card number
        listC[4] = converter(InputList[7]) #birthdate
        listC[5] = ["".join(list(map(lambda x: x.lower(),InputList[8])))] #passport number
        listC[6] = InputList[1] #type
            
            
            
            
        listCC[0] = DBList[j][2]                                          # name
        if len(DBList[j][4])>1:                                           # nationality
            listCC[1] = (list(map(lambda x: x.lower(),DBList[j][4])))
        else:
            listCC[1] = ["".join(list(map(lambda x: x.lower(),DBList[j][4])))] 
                
        if len(DBList[j][5])>1:                                           # address
            listCC[2] = (list(map(lambda x: x.lower(),DBList[j][5])))
        else:
            listCC[2] = ["".join(list(map(lambda x: x.lower(),DBList[j][5])))] 
           
        if len(DBList[j][6])>1:                                           # id card number
            listCC[3] = (list(map(lambda x: x.lower(),DBList[j][6])))
        else:
            listCC[3] = ["".join(list(map(lambda x: x.lower(),DBList[j][6])))] 
           
        listCC[4] = converter(DBList[j][7])                               # birthdate
            
        if len(DBList[j][8])>1:                                           # passport number
            listCC[5] = (list(map(lambda x: x.lower(),DBList[j][8])))
        else:
            listCC[5] = ["".join(list(map(lambda x: x.lower(),DBList[j][8])))] 
           
        listCC[6] = DBList[j][1]                                          # type

            
        if str(listCC[6]) == str(listC[6]):
            finalList.append([round(resemblanceToData(listC,listCC),2), DBList[j]
                                    [0], (DBList[j][2])])
        if len(finalList) == 0:
              return None   
    df = (pd.DataFrame((finalList), columns = column_set)).sort_values(by = "rate", ascending = False)
    return df

print(np.array(csvCompare(inputList, DBList )))
with open("jsonComparaisonFile.json", "w", encoding='utf-8') as j:
    json.dump(csvCompare(inputList, DBList ).to_json(orient = "records"),j,ensure_ascii=False, indent=4 )
#data = (csvCompare(inputList, DBList )).to_json("./jsonComparaisonFileV1", orient = "records")
print("---%s seconds ---" % (time.time() - start_time))
#s = input("")


