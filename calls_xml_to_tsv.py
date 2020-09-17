#########################################
# .: calls_xml_to_tsv.py :.
# Parses a calls xml backup file from Android app SMS Backup and Restore, parses out select data and generates a TSV file
# Usage: python3 calls_xml_to_tsv.py <your_sms_xml_file>
# eg: python3 calls_xml_to_tsv.py calls-20200917002015.xml
# .: Other :.
# Author: Timothy C. Quinn
# Home: <tbd>
# Licence: https://opensource.org/licenses/MIT
#########################################
import os, csv, traceback, sys
from xml.etree.ElementTree import parse as parse_xml
import common as smr
pc = smr.pc

def main(argv):

    try:

        (sFile) = smr.loadArgs(argv, 'calls')

        sFilePrefix = sFile

        aColumns = ['year', 'mon', 'day', 'time', 'dur(m)', 'contact', 'phone', 'type']

        out_fname = 'z_{}.tsv'.format(sFilePrefix)
           
        tree = parse_xml(sFile)

        calls = tree.getroot()

        pc("""Backup info: 
  File: {}
  count={}
  backup_set={}
  backup_date={}""".format(
    sFile, calls.get('count'), calls.get('backup_set'), calls.get('backup_date')))

        rows = []; iC = 0
        for m in calls.findall('call'):
            iC = iC + 1
            # pc('type(m) = {}', type(m))
            # pc('m = {}', smr.dump(m, True))

            iType = smr.aget("m", m, 'type', req=True, toint=True)
            if iType == 1:
                sType = "1"
            elif iType == 2:
                sType = "2"
            elif iType == 3:
                sType = "3"
            elif iType == 5:
                sType = "5"
            else:
                raise Exception("Unexpected type {} in xml: {}".format(iType, smr.dump(m)))

            sPhone = smr.fixPhone(smr.aget("m", m, 'number', req=True))
            
            rows.append([
                 *smr.parseDate(smr.aget("m", m, 'readable_date', req=True))
                ,round(smr.aget("m", m, 'duration', req=True, toint=True)/60, 1)
                ,smr.aget("m", m, 'contact_name', req=True)
                ,sPhone
                ,sType
                
            ])

        pc("calls found: {}", iC)


        # Sort
        rows = sorted(rows, key=lambda r: (r[0], r[1], r[2], r[3]) )

        fTmp = open(out_fname,'w', newline='')
        bNewFile=True
        wri = csv.writer(fTmp, delimiter='\t')
        wri.writerow(aColumns)

        for r in rows:
            wri.writerow(r)

        fTmp.close()

        pc("Data written to: {}".format(out_fname))

        pc('.: done :.')
        pc('.')


    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        sTB = '\n'.join(traceback.format_tb(exc_traceback))
        pc("Fatal exception: {}\n - msg: {}\n stack: {}".format(exc_type, exc_value, sTB))


if __name__ == '__main__':
    main(sys.argv[1:])
