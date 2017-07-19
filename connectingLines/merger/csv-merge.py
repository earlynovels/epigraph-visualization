import csv

# File without END 700s fields
oldFile = 'full-epigraphs.tsv'
# File with END 700s fields (without full epigraphs included)
authFile = 'full-epigraph-authors.tsv'
# File to write to: for superset of two previous files
newFile = 'newfile.tsv'

# reads in CSV and creats list of all row content, and separate list
# of all IDs in that CSV
def makeIDsList(theFile, key):
    ids = []
    rows = []
    # open with universal newline (and read mode) to avoid a quoting error
    with open(theFile, 'rU') as oldtsvfile:
          reader = csv.DictReader(oldtsvfile, dialect='excel-tab', quoting=csv.QUOTE_ALL)
          for row in reader:
              ids.append(row['id'])
              # set a new d field, depending on what new key was passed in 
              row[key] = row['d']
              rows.append(row)
    return ids, rows

# auth = ['id', 'title', 'author', 'date', 'epigraph-author', 'd', '5']
# old = ['id', 'title', 'short_title', 'author', 'date', 'a', 'd', '1', 'b', '2', 'c', 'x', 'v']

# Searches in list of dictionaries for a dictionary with an id matching param: idNum
def search(idNum, dict_list):
    return [item for item in dict_list if item['id'] == idNum]

# Writes out to newFile defined at top: takes data from auth file if available, otherwise from old file
def makeNewFile(IDs, old, auth, newfile):
    old_sort = sorted(old, key=lambda k: k['id'])
    auth_sort = sorted(auth, key=lambda k: k['id'])
    ## Proof that sort works
    # print [item['id'] for item in old_sort] == sorted([item['id'] for item in old_sort])
    # print [item['id'] for item in auth_sort] == sorted([item['id'] for item in auth_sort])
    with open(newfile, 'w') as tsvfile:
        try:
            # see if short titles exist in either file, and need to be pulled
            check = old[0]['short_title']
            check2 = auth[0]['short_title']
            # include short_title in field names if it exists
            fieldnames = ['id', 'title', 'short_title', 'author', 'date', 'epigraph_author', 'd1', '5', 'a', 'd2', '1', 'b', '2', 'c', 'x', 'v']
        except KeyError:
            # write fieldnames without short_title otherwise
            fieldnames = ['id', 'title', 'author', 'date', 'epigraph_author', 'd1', '5', 'a', 'd2', '1', 'b', '2', 'c', 'x', 'v']

        writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        # write file in sorted order of set of IDs from both files
        for i in range(len(IDs)):
            each_row = {}
            # If DEBUG statements are uncommented, prints out a short summary of process for each field (for each ID)
            # Try to use field info from auth first if possible. If not, use old. If it only exists in old, fill in blanks for missing fields
            for field in fieldnames:
                # print ## DEBUG
                # print "new" ## DEBUG
                try:
                    idDict = search(IDs[i], auth_sort)
                    # if len(idDict) != 1:
                        # print "Work not found in auth", IDs[i] ## DEBUG
                    # print "AUTH", idDict, field, IDs[i] ## DEBUG
                    each_row[field] = idDict[0][field]
                except (KeyError, IndexError) as ListError:
                    # print type(ListError) ## DEBUG
                    idDict = search(IDs[i], old_sort)
                    # if len(idDict) != 1:
                        # print "Work not found in old", IDs[i] ## DEBUG
                    # print "OLD", idDict, field, IDs[i] ## DEBUG
                    try:
                        each_row[field] = idDict[0][field]
                        # print each_row[field] ## DEBUG
                    except (KeyError, IndexError) as ListError:
                        each_row[field] = ""
                        # print "" ## DEBUG
            writer.writerow(each_row)

def main():
    oldIDs, oldRows = makeIDsList(oldFile, 'd2')
    authIDs, authRows = makeIDsList(authFile, 'd1')

    totalIDs = sorted(list(set(oldIDs + authIDs)))
    makeNewFile(totalIDs, oldRows, authRows, newFile)

main()
