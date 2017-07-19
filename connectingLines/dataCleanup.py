# -*- coding: latin-1 -*-

import requests
import re
import csv
import json
import io
import string
import argparse
from bs4 import BeautifulSoup


### GLOBAL
queryCounter = 0
manualAdditionsAuthors = []
manualAdditionsDates = []
# Add strings here to include them in the parser for the CLI manual check
manualSeparators = [',', ' of ', ' in ', ' a ', ' an ', '.', ' to ', ' In ']
# Names of files to use
titlesInputFile = 'datesComplete.tsv'
titlesOutputFile = 'datesAndTitlesComplete.tsv'


def searchDateRange(result, given):
    for i in range(len(result)-1,-1,-1):
        try:
            if result[i].isdigit() and result[i-1].isdigit() and result[i-2].isdigit() and result[i-3].isdigit():
                trueResult = result[i-3]+result[i-2]+result[i-1]+result[i]
                return trueResult
        except IndexError:
            if not given:
                return -1
    if not given:
        return -1
    else:
        if result not in manualAdditionsAuthors:
            manualResult = raw_input("What should this date be ("+result.encode("latin-1")+"): ")
            # manualResult = ""
            if (manualResult == ""):
                manualResult = "null"
            else:
                manualAdditionsAuthors.append(result)
                manualAdditionsDates.append(manualResult)
            return manualResult
        else:
            index = manualAdditionsAuthors.index(result)
            return manualAdditionsDates[index]

# https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

# can be used as standalone function to get author (birth) date
# input: author name (to be used as query string)
# output: first date in author date range
def viafParser(author):
    global queryCounter
    queryCounter += 1
    author = author.strip('\'\"\[\].')
    url = 'http://viaf.org/viaf/AutoSuggest?query=' + author
    r = requests.get(url)
    try:
        doc = r.json()
    except ValueError:
        doc = r.text
        new_author = ""
        for char in author:
            if char == "\'" or char == '\"':
                pass
            else:
                new_author += char
        new_author = new_author.strip('\'\"\[\].')
        url = 'http://viaf.org/viaf/AutoSuggest?query=' + new_author
        r = requests.get(url)
        queryCounter += 1
        doc = r.json()

    if doc['result'] == None or doc['result'] == "null":
        return "null"
    for i in range(len(doc['result'])):
        result = doc['result'][i]['displayForm']
        date = searchDateRange(result, False)
        if date != -1:
            return date
        elif hasNumbers(result):
            if result not in manualAdditionsAuthors:
                manualResult = raw_input("What should this date be ("+result+"): ")
                # manualResult = ""
                if (manualResult == ""):
                    manualResult = "null"
                else:
                    manualAdditionsAuthors.append(result)
                    manualAdditionsDates.append(manualResult)
                return manualResult
            else:
                index = manualAdditionsAuthors.index(result)
                return manualAdditionsDates[index]
        else:
            return "null"

def wikiParser(name):
    redirectedList = []
    url = 'http://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&rvsection=0&titles='+name+'&format=xml'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "xml")

    try:
        death_re = re.search(r'(Death date(.*?)}})', soup.revisions.getText())
        if death_re == None:
            death_re = re.search(r'(Death date(.*?)}})', soup.revisions.getText())
        death_data = death_re.group(0).split('|')
        death_year = death_data[2]
        return death_year,name
    except AttributeError:
        try:
            # read from "death_date" to ")"
            death_re = re.search(r'(death_date(.*?)(?=\())', soup.revisions.getText())
            numbersList = []
            death_data = death_re.group(0)
            for i in range(len(death_data)-1,-1,-1):
                if death_data[i].isdigit():
                    numbersList.append(death_data[i])
                    for j in range(i-1,-1,-1):
                        if death_data[j].isdigit():
                            numbersList.append(death_data[j])
                        else:
                            numbersList.reverse()
                            numbersList.append(death_data[i+1:])
                            return ''.join(numbersList),name
            return death_data,name
        except:
            try:
                # redirect?
                redirectRe = re.search(r'#REDIRECT(.*?)(?=\])', soup.revisions.getText())
                redirect_name = redirectRe.group(0)
                if (redirect_name not in redirectedList):
                    redirectedList.append(redirect_name)
                    nameList = []
                    for i in range(len(redirect_name)-1,-1,-1):
                        if (redirect_name[i]!='['):
                            nameList.append(redirect_name[i])
                        else:
                            nameList.reverse()
                            newName = ''.join(nameList)
                            return wikiParser(newName)
                else:
                    return "null", name
            except:
                return "null", name

def parseName(name):
    for character in ['[',']','\'','\"']:
        name = name.replace(character,'')
    index = name.find(',')
    if (index != -1):
        name = name[index+2:]+" "+name[:index]
    return name

def parseFile():
    targetFile = open("datesComplete.tsv","w")
    with io.open("initialCombined.tsv", "r", encoding="latin-1") as inputFile:
        # data = inputFile.read()
        lineNum = 1
        tab = "\t"
        # id	title	author	date	epigraph_author	d1	5	a	d2	1	b	2	c	x	v
        # build up source and target lists and write first line to file
        for i, line in enumerate(inputFile):
            lineList = line.strip("\n").split(tab)
            # priority: epigraphAuthorCol (d1Col), cCol, twoCol
            for i in range(len(lineList)):
                # word.decode("latin-1").replace(u'\u200f', u'').encode("latin-1")
                if "\u200f" in lineList[i].encode('latin-1'):
                    # word.replace("\u200f","")
                    theIndex = (lineList[i].encode('latin-1')).index("\u200f")
                    lineList[i] = (lineList[i].encode('latin-1'))[:theIndex]+"']"

            lineList[2] = parseName(lineList[2])

            idCol = lineList[0]
            if lineList[1] == '':
                try:
                    lineList[1] = previous[1]
                except:
                    continue
            titleCol = lineList[1]
            authorCol = lineList[2]
            dateCol = lineList[3]
            epigraphAuthorCol = lineList[4]
            d1Col = lineList[5]
            fiveCol = lineList[6]
            aCol = lineList[7]
            d2Col = lineList[8]
            oneCol = lineList[9]
            bCol = lineList[10]
            twoCol = lineList[11]
            cCol = lineList[12]
            xCol = lineList[13]
            vCol = lineList[14]
            immutableElements = '\t'.join(lineList)
            priorityAuthorArray = []
            priorityDateArray = []
            allBlank = True
            if (lineNum==1):
                targetFile.write(immutableElements.encode("latin-1")+tab+"new_ep_author_col"+tab+"new_ep_date_col"+"\n")
            else:
                targetFile.write(immutableElements.encode("latin-1")+tab)
                allBlank = True
                if epigraphAuthorCol != "":
                    allBlank = False
                    new_ep_author_col = parseName(epigraphAuthorCol)
                    priorityAuthorArray.append(new_ep_author_col)
                    if d1Col != "":
                        currDate = searchDateRange(d1Col,True)
                        if currDate == -1:
                            currDate = "null"
                        priorityDateArray.append(currDate)
                    else:
                        priorityDateArray.append(viafParser(new_ep_author_col))
                if cCol != "":
                    allBlank = False
                    new_ep_author_col = parseName(cCol)
                    priorityAuthorArray.append(new_ep_author_col)
                    priorityDateArray.append(viafParser(new_ep_author_col))
                if twoCol != "":
                    allBlank = False
                    new_ep_author_col = parseName(twoCol)
                    priorityAuthorArray.append(new_ep_author_col)
                    priorityDateArray.append(viafParser(new_ep_author_col))
                if allBlank==True:
                    priorityAuthorArray.append("null")
                    priorityDateArray.append("null")

                firstAuthor = True
                firstDate = True
                for i in range(len(priorityDateArray)):
                    author = priorityAuthorArray[i]
                    date = priorityDateArray[i]
                    if author != "null" and firstAuthor==True:
                        correctAuthor = author
                        firstAuthor = False
                        if (date != "null" and firstDate==True):
                            correctDate = date
                            firstDate = False
                if (firstDate==True and firstAuthor==False):
                    for eachAuthor in priorityAuthorArray:
                        correctDate,parsedAuthor = wikiParser(eachAuthor)
                        if (correctDate != "null"):
                            # can't be after publishing date
                            try:
                                if int(correctDate) < int(dateCol):
                                    correctAuthor = parsedAuthor
                                    break
                            except:
                                correctAuthor = parsedAuthor
                                break
                if (correctDate != "null"):
                    # can't be after publishing date
                    try:
                        if int(correctDate) > int(dateCol) or int(correctDate) > 1800:
                            for eachAuthor in priorityAuthorArray:
                                correctDate,parsedAuthor = wikiParser(eachAuthor)
                                if int(correctDate) < int(dateCol) and int(correctDate) < 1800:
                                    break
                        if len(priorityAuthorArray) == 0:
                            correctAuthor = "null"
                            correctDate = "null"
                        if int(correctDate) > int(dateCol) or int(correctDate) > 1800:
                            correctDate = "null"
                    except:
                        pass

                if (firstAuthor==True):
                    targetFile.write("null".encode('latin-1')+tab+"null".encode('latin-1')+"\n")
                else:
                    if "BC" in correctDate:
                        index = correctDate.index("BC")
                        correctDate = correctDate[:index]
                        correctDate = correctDate.strip(' ')
                        correctDate = '-'+correctDate
                    if "<br/>" in correctDate:
                        index = correctDate.index("<br/>")
                        correctDate = correctDate[:index]

                    targetFile.write(correctAuthor.encode('latin-1')+tab+correctDate.encode('latin-1')+"\n")
            lineNum+=1
            previous = lineList


def readTitles(fileName):
    titles = []
    rows = []
    short_titles = []
    with open(fileName, "rU") as tsvfile:
    # file_read = csv.DictReader(self.file, dialect=csv.excel_tab)
      reader = csv.DictReader(tsvfile, dialect='excel-tab')
      for row in reader:
        # Deletes empty titles
        try:
            blah = row['short_title']
            short_titles.append(blah)
        except KeyError:
            short_titles.append("")

        if row['title'] != '':
            titles.append(row['title'])
            rows.append(row)
    return titles, short_titles, rows

# Shorten sentences with period partition
def stripSentenceEnds(title):
    if "." in title[:50]:
        honorifics = re.findall(r"\ [A-Z][a-z]\.", title[:50])
        if len(honorifics) < title[:50].count('.'):
            title, sep, discard = title[:50].rpartition(".")
            if title == "":
                title = discard
    return title

# Parse a single title into short version by the automatic separators
def parseOne(title):
    separators = ['by', 'By', 'a novel', 'A novel', ';', ':', ' or ', 'Vol', 'vol']
    count = 0
    found = False
    title = stripSentenceEnds(title)

    while found != True:
        title, sep, discard = title.partition(separators[count])
        count += 1
        if count >= len(separators):
            if len(title) > 41:
                title, sep, discard = title[:50].rpartition(",")
                if title == "":
                    title = discard
            if len(title) > 41:
                index = 40
                while index != len(title)-1 and title[index].isalpha():
                    if index + 1 < len(title):
                        index += 1
                title = title[:index+1]
            found = True

    # strip whitespace and any trailing punctuation from title before returning
    return title.strip().rstrip(string.punctuation)

# Iterates through all longform titles, calls parseOne to shorten each
def parseTitles(oldTitles, short_titles):
    newTitles = []
    for i in range(len(oldTitles)):
        if short_titles[i] != "":
            newTitles.append(short_titles[i])
        else:
            newTitles.append(parseOne(oldTitles[i]))
    return newTitles

# Returns boolean to indicate whether one of second set of separators is
# contained in title. Called on already shortened titles
def triggerInTitle(title, char_list):
    for sep in char_list:
        if sep in title:
            return True
        else:
            pass
    return False

# Creates list of alternate short tiles based on second set of separators
# for manual checking
def altList(title, seps):
    alternates = [title]
    for i in range(len(seps)):
        newtitle, sep, discard = title.partition(seps[i])
        alternates.append(newtitle)
    return alternates

# Manual title editor interface
def manualTitle(oldtitle, title, seps):
    i = 0
    continueCheck = True
    if triggerInTitle(title,seps):
        print "\n" + "Long title: " + oldtitle + "\n"
        print "Short title: " + title + "\n"
        print "Title options: "
        alternates = list(set(altList(title, seps)))
        for alt in alternates:
            print i, "\t", alt
            i += 1
        print i, "Write your own. "
        print "If none of these numbers are chosen,",
        print "the original short title will be used. "
        print "To stop checking manually, and start automating, enter the letter n. "
        print "To stop checking manually, and resume later, type end"
        answer = raw_input("Which title should be used? ")
        choice = answer.strip()
        if choice.isdigit():
            choice = int(choice)
            if choice < len(alternates):
                print alternates[choice]
                return alternates[choice], True, False
            else:
                 return raw_input("What should the title be?"), True, False
        elif choice == "n":
            print title
            return title, False, False
        elif choice == "end":
            return "", True, True
        else:
            print title
            return title, True, False
    else:
        return title, True, False

# Writes new TSV file with shortened titles column
def writeFile(fileName, shortTitles, rows, manual, cont):
    with open(fileName, 'w') as csvfile:
        fieldnames = ['id', 'title', 'author', 'date', 'epigraph_author', 'd1', '5', 'a', 'd2', '1', 'b', '2', 'c', 'x', 'v', 'new_ep_author_col', 'new_ep_date_col', 'short_title']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="\t")

        writer.writeheader()
        used_titles = {}
        end = False
        for i in range(len(rows)):
            if manual == True:
                if end == True:
                    title = ""
                else:
                    #cont is whether it's starting with a file that already has some short titles
                    if cont == True:
                        try:
                            title = rows[i]['short_title']
                        except KeyError:
                            # LIES
                            print("Exiting parser; check arguments and try again. -c flag not applicable on input file.")
                            break
                        if title == "":
                            title, manual, end = manualTitle(rows[i]['title'], shortTitles[i], manualSeparators)

                    else:
                        title, manual, end = manualTitle(rows[i]['title'], shortTitles[i], manualSeparators)
                                 # non-manual and not wrting blanks
            else: #manual is false
                title = shortTitles[i]
            rows[i]['short_title'] = title
            writer.writerow(rows[i])

def writeSimpleFile():
    finalFile = open(titlesOutputFile,"r")
    targetFile = open("parsedData.tsv","w")
    lineNum = 1
    tab = "\t"

    # build up source and target lists and write first line to file
    for line in finalFile:
        if (lineNum==1):
            categories = "ident\tid\tidAuthor\ttarget\tidDate\ttargetDate\n"
            targetFile.write(categories)
        else:
            lineList = line.strip("\n")
            lineList = lineList.strip("\r")
            lineList = lineList.split(tab)
            # set variables
            ident=lineList[0]
            shortTitle=lineList[17].rstrip('.')
            author=lineList[2]
            author = author.decode('latin-1').encode('ascii',errors='ignore').rstrip('.')

            pubDate=lineList[3].rstrip('.')
            epAuthor = lineList[15]
            epAuthor = epAuthor.decode('latin-1').encode('ascii',errors='ignore').rstrip('.')
            epigraph=lineList[7]
            for character in ['[',']','\'','\"']:
                epigraph = epigraph.replace(character,'')
                shortTitle = shortTitle.replace(character,'')
                author = author.replace(character,'')
            if ',' in author:
                index = author.find(',')
                if (index != -1):
                    author = author[index+2:]+" "+author[:index]
            epAuthorDate = lineList[16]
            if epAuthorDate == "null":
                epAuthorDate = "5000"
            if (author == ""):
                author = "null"
            if (epAuthor!="" and epAuthor!="null" and any(c.isalpha() for c in epAuthor)):
                targetFile.write(ident+tab+shortTitle+tab+author+tab+epAuthor+tab+pubDate+tab+epAuthorDate+"\n")
        lineNum +=1
# read in csv
def main():
    parser = argparse.ArgumentParser(description="allows manual title checking")
    parser.add_argument('-m', '--manual', help="run manual title checker", action="store_true")
    parser.add_argument('-c', '--continuing', help="start prev file from where left off", action="store_true")
    parser.add_argument('-d', '--dates', help="generate dates", action="store_true")
    args = parser.parse_args()
    if (args.dates == True):
        parseFile()
    titles, short_titles, rows = readTitles(titlesInputFile)
    shortTitles = parseTitles(titles, short_titles)
    writeFile(titlesOutputFile, shortTitles, rows, args.manual, args.continuing)
    writeSimpleFile()



if __name__ == "__main__": main()
