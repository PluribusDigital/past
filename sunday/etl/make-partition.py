import csv
import io
import os
import sys
import zipfile
import multiprocessing as mp
from collections import Counter
from itertools import islice
from functools import partial

SOURCE_DIR = './source'
PARTITION_DIR = './partitions'
SEED_DIR = '../db/seed'

TENK = 10000
HUNDREDK = 100000
MILLION = 1000000

# -----------------------------------------------------------------------------

def idSort(x):
    try:
        return (int(x), x)
    except:
        return (sys.maxsize, x)

def kvpValue(kvp):
    return kvp[1]

# -----------------------------------------------------------------------------

def acquireZipped(fileName, dialect='excel-tab', encoding='iso-8859-1'):
    file = os.path.join(SOURCE_DIR, fileName)
    with zipfile.ZipFile(file, allowZip64=True) as zip:
        name = zip.namelist()[0]
        with zip.open(name, "r") as f:
            wrapped = io.TextIOWrapper(f, newline="", encoding=encoding)
            reader = csv.DictReader(wrapped, dialect=dialect)
            for row in reader:
                yield row

def tally(titleFile, tallyFile, tallyField, outputFile):
    print(tallyFile, '...')

    print('  titles')
    titles = {x['id']:x['title'] for x in acquireZipped(titleFile)}

    print('  tallying')
    fn = map(lambda x: x[tallyField], acquireZipped(tallyFile))
    tally = Counter(fn)

    print('  output')
    fileName = os.path.join(SEED_DIR, outputFile)
    with open(fileName, 'w') as f:
        f.write(tallyField)
        f.write('\ttitle\tcount\n')
        for k,v in sorted(tally.items(), key=kvpValue, reverse=True):
            f.write('{0}\t{1}\t{2}\n'.format(k,
                                             titles[k] if k in titles else k,
                                             tally[k]))

# -----------------------------------------------------------------------------
# Partition Methods
# -----------------------------------------------------------------------------

cpcTopTen = {'H01L', 'Y10T', 'G06F', 'H04N', 'H04L',
             'A61K', 'A61B', 'Y10S', 'C07C', 'G11B'}

uspcTopTen = {'257', '428', '514', '435', '438', 
              '455', '370', '424', '348', '375'}

def partitionFileName(fileName='partition.txt'):
    return os.path.join(PARTITION_DIR, fileName)

def generatePatentIds(keyField, values, fileName):
    ''' Builds a subset of patents that fall within particular categories and ranges
    '''
    inner = islice(acquireZipped(fileName), MILLION * 2)
    for row in inner:
        if row[keyField] in values:
            try:
                i = int(row['patent_id'][0:3])
                # The first patents issued in 2007 started with 765
                # Take every 17th one from that point on
                if i > 765 and int(row['patent_id']) % 17 == 0:
                    yield row['patent_id']
            except:
                pass

def createPartition():
    print('Getting list of patents')
    patents = set(generatePatentIds('group_id', cpcTopTen, 'cpc_current.zip'))

    with open(partitionFileName(), 'w') as f:
        for patent in sorted(patents):
            f.write('{0}\n'.format(patent));

def loadPartition():
    with open(partitionFileName(), 'r') as f:
        for line in f:
            yield line.strip()

    with open(partitionFileName('prior-art.txt'), 'r') as f:
        for line in f:
            yield line.strip()

# -----------------------------------------------------------------------------
# Seed-* methods
# -----------------------------------------------------------------------------

def seedFileName(source):
    from os import path
    return path.join(SEED_DIR, 'seed-{0}.txt'.format(source.replace('_', '-')))

def buildSeed(ids, source, fields, idField='patent_id'):
    encoding = 'utf8'
    fileName = seedFileName(source)
    
    with open(fileName, 'w', encoding=encoding, newline='') as f:
        writer = csv.DictWriter(f, fields, dialect='excel-tab', 
                                extrasaction='ignore')
        writer.writeheader()

        i = 0
        j = 1
        for row in acquireZipped(source + '.zip'):
            i += 1
            if row[idField] in ids:
                writer.writerow(row)
            if i == HUNDREDK:
                print('  {0} {1} x 100K'.format(source, j))
                i = 0
                j += 1

relPatent = {
             'application': ['id', 'patent_id', 'series_code', 'number',
                             'country','date'],
             'claim': ['uuid', 'patent_id', 'text', 'dependent', 'sequence'],
             'cpc_current': ['uuid', 'patent_id', 'section_id', 'subsection_id',
                             'group_id', 'subgroup_id', 'category', 
                             'sequence'],
             'rawassignee': ['uuid', 'patent_id', 'assignee_id', 
                             'rawlocation_id', 'type', 'name_first', 
                             'name_last', 'organization', 'sequence'],
             'rawinventor': ['uuid', 'patent_id', 'inventor_id', 
                             'rawlocation_id', 'name_first', 'name_last', 
                             'sequence'],
             'rawlawyer': ['uuid', 'lawyer_id', 'patent_id', 'name_first', 
                           'name_last', 'organization', 'country', 'sequence'],
             'patent': ['id', 'type', 'number', 'date', 'kind', 'abstract', 
                        'title'],
             #'usapplicationcitation': ['uuid', 'patent_id', 'application_id',
             #                          'date', 'kind', 'number', 'country',
             #                          'category', 'sequence'],
             'uspatentcitation' : ['uuid', 'patent_id', 'citation_id', 'date',
                                   'name', 'kind', 'country', 'category',
                                   'sequence'],
             'uspc_current': ['uuid', 'patent_id', 'mainclass_id',
                              'subclass_id', 'sequence']
           }

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def worker(ids, k):
    if not os.path.exists(seedFileName(k)):
        buildSeed(ids, k, relPatent[k], 
                  'number' if k == 'patent' else 'patent_id')

if __name__ == '__main__':
    if not os.path.exists(partitionFileName()):
        createPartition()

    # Fill the queue
    ids = {x for x in loadPartition()}

    bind = partial(worker, ids)

    # start 4 worker processes
    with mp.Pool(processes=4) as pool:
        pool.map(bind, sorted(relPatent))
