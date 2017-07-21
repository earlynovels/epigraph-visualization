inputFile = open("parsedData.tsv","r")
authorFile = open("authorship.tsv","r")
targetFile = open("gendered.tsv","w")
tab = "\t"

def countGenders():
   otherLineNum = 1
   maleCounter = 0
   femaleCounter = 0
   authorFile.seek(0)
   for otherLine in authorFile:
      if otherLineNum != 1:
         lineListAuthor = otherLine.strip("\n").strip("\r").split(tab)
         genderClaim = lineListAuthor[8][2:-2]
         if genderClaim.lower() == "male":
            maleCounter += 1
         if genderClaim.lower() == "female":
            femaleCounter += 1
      otherLineNum += 1
   return maleCounter,femaleCounter


def checkForMatch(identInput):
   otherLineNum = 1
   authorFile.seek(0)
   for otherLine in authorFile:
      if otherLineNum != 1:
         lineListAuthor = otherLine.strip("\n").strip("\r").split(tab)
         identAuthor = lineListAuthor[0]
         if identInput == identAuthor:
            genderClaim = lineListAuthor[8][2:-2]
            if genderClaim.lower() != "male" and genderClaim.lower() != "female":
               return "null"
            return genderClaim
      otherLineNum += 1
   return "null"

def main():
   listOfLinesFinal = []
   firstWrite = True
   totalMale,totalFemale = countGenders()
   epMaleCounter = 0
   epFemaleCounter = 0
   lineNum = 1
   for line in inputFile:
      if lineNum == 1:
         targetFile.write("ident\tid\tidAuthor\ttarget\tidDate\ttargetDate\tgender\ttotalMale\ttotalFemale\tepMale\tepFemale\tpercentMale\tpercentFemale\n")
      else:
         lineListInput = line.strip("\n").strip("\r").split(tab)
         identInput = lineListInput[0]
         genderClaim = checkForMatch(identInput)
         if genderClaim != "null":
            if genderClaim.lower() == "male":
               epMaleCounter += 1
            elif genderClaim.lower() == "female":
               epFemaleCounter += 1
            if firstWrite:
               firstWrite = False
               listOfLinesFinal.append(lineListInput[0]+tab+lineListInput[1]+tab+lineListInput[2]+tab+lineListInput[3]+tab+lineListInput[4]+tab+lineListInput[5]+tab+genderClaim+tab+str(totalMale)+tab+str(totalFemale)+"\n")
            else:
               listOfLinesFinal.append(lineListInput[0]+tab+lineListInput[1]+tab+lineListInput[2]+tab+lineListInput[3]+tab+lineListInput[4]+tab+lineListInput[5]+tab+genderClaim+"\n")
      lineNum += 1
   for i in range(len(listOfLinesFinal)):
      if i == 0:
         line = listOfLinesFinal[i].strip("\n")
         lineSplit = line.split('\t')
         percentMale = epMaleCounter/float(lineSplit[7])*100
         percentFemale = epFemaleCounter/float(lineSplit[8])*100
         percentMod = 100/float(percentMale+percentFemale)
         percentMale = percentMale * percentMod
         percentFemale = percentFemale * percentMod
         line += tab+str(epMaleCounter)+tab+str(epFemaleCounter)+tab+str(percentMale)+tab+str(percentFemale)+"\n"
      else:
         line = listOfLinesFinal[i]
      targetFile.write(line)
if __name__ == '__main__':
   main()
