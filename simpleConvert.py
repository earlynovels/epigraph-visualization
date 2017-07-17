# -*- coding: UTF-8 -*-

def main():
    file = open("continue.tsv","r")
    targetFile = open("graph1.tsv","w")
    lineNum = 1
    tab = "\t"

    # build up source and target lists and write first line to file
    for line in file:
        if (lineNum==1):
            categories = "id\tidAuthor\ttarget\tidDate\ttargetDate\n"
            targetFile.write(categories)
        else:
            lineList = line.strip("\n")
            lineList = lineList.strip("\r")
            lineList = lineList.split(tab)
            # set variables
            ident=lineList[0]
            longTitle=lineList[1]
            author=lineList[2]
            author = author.decode('utf-8').encode('ascii',errors='ignore')
            pubDate=lineList[3]
            epAuthor = lineList[15]
            epAuthor = epAuthor.decode('utf-8').encode('ascii',errors='ignore')
            epigraph=lineList[7]
            for character in ['[',']','\'','\"']:
                epigraph = epigraph.replace(character,'')
                longTitle = longTitle.replace(character,'')
            epAuthorDate = lineList[16]
            if epAuthorDate == "null":
                epAuthorDate = "5000"
            shortTitle=lineList[17]
            if (author == ""):
                author = "null"
            if (epAuthor!="" and epAuthor!="null"):
                targetFile.write(shortTitle+tab+author+tab+epAuthor+tab+pubDate+tab+epAuthorDate+"\n")
        lineNum +=1

if __name__ == "__main__": main()
