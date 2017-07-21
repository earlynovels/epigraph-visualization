from collections import defaultdict
inputFile = open("parsedData.tsv","r")
targetFile = open("shakespeareDecade.csv","w")
targetDict = defaultdict(int)
tab = "\t"

lineNum = 1
for line in inputFile:
  if lineNum == 1:
     targetFile.write("date,number\n")
  else:
    lineList = line.strip("\n").strip("\r").split(tab)
    ident = lineList[0]
    title = lineList[1]
    author = lineList[2]
    epAuthor = lineList[3]
    pubDate = lineList[4]
    epAuthorDate = lineList[5]
    if "shakespeare" in epAuthor.lower():
      try:
        pubDate = int(pubDate)
        if pubDate < 1710:
          targetDict["1700"] += 1
        elif pubDate < 1720:
          targetDict["1710"] += 1
        elif pubDate < 1730:
          targetDict["1720"] += 1
        elif pubDate < 1740:
          targetDict["1730"] += 1
        elif pubDate < 1750:
          targetDict["1740"] += 1
        elif pubDate < 1760:
          targetDict["1750"] += 1
        elif pubDate < 1770:
          targetDict["1760"] += 1
        elif pubDate < 1780:
          targetDict["1770"] += 1
        elif pubDate <= 1790:
          targetDict["1780"] += 1
      except:
        pass
  lineNum += 1
dateRange = range(1700,1791,10)
for key in dateRange:
  key = str(key)
  targetFile.write(key+","+str(targetDict[key])+"\n")
