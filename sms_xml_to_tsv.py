#########################################
# .: calls_xml_to_tsv.py :.
# Parses a sms xml backup file from Android app SMS Backup and Restore, parses out select data and generates a TSV file
# Usage: python3 sms_xml_to_tsv.py <your_sms_xml_file>
# eg: python3 sms_xml_to_tsv.py sms-20200917002015.xml
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

        (sFile) = smr.loadArgs(argv, "sms")

        sFilePrefix = sFile

        # First lets write SMS
        aColumns = ['type', 'year', 'mon', 'day', 'time', 'contact', 'phone', 'dir', 'body']

        out_fname = 'z_{}.tsv'.format(sFilePrefix)
            
        tree = parse_xml(sFile)

        smses = tree.getroot()

        rows = []; iC = 0
        for m in smses.findall('sms'):
            iC = iC + 1
            # pc('type(m) = {}', type(m))
            # pc('m = {}', smr.dump(m, True))

            iType = smr.aget("m", m, 'type', req=True, toint=True)
            if iType == 1:
                sType = "in"
            elif iType == 2:
                sType = "out"
            else:
                raise Exception("Unexpected type {} in xml: {}".format(iType, smr.dump(m)))

            sPhone = smr.fixPhone(smr.aget("m", m, 'address', req=True))
            
            rows.append([
                 'sms'
                ,*smr.parseDate(smr.aget("m", m, 'readable_date', req=True))
                ,smr.aget("m", m, 'contact_name', req=True)
                ,sPhone
                ,sType
                ,smr.aget("m", m, 'body', req=True)
                
            ])

        pc("sms records found: {}", iC)

        iC = 0
        for m in smses.findall('mms'):
            # pc('type(m) = {}', type(m))
            # pc('m = {}', smr.dump(m, True))
            iType = smr.aget("m", m, 'type', req=True, toint=True)
            if iType == -1:
                sType = "?"
            else:
                raise Exception("Unexpected type {} in xml: {}".format(iType, smr.dump(m)))

            sPhone = smr.fixPhone(smr.aget("m", m, 'address', req=True))

            sMsg = ""
            for part in m.findall('part'):
            # for part in m.find('parts').getchildren():
                iSeq = smr.aget("part", part, 'seq', req=True, toint=True)
                if iSeq == 0:
                    sMsg = smr.aget("part", part, 'text', req=True)

            
            rows.append([
                 'mms'
                ,*smr.parseDate(smr.aget("m", m, 'readable_date', req=True))
                ,smr.aget("m", m, 'contact_name', req=True)
                ,sPhone
                ,sType
                ,sMsg
            ])

        pc("mms records found: {}", iC)

        # Sort
        rows = sorted(rows, key=lambda r: (r[1], r[2], r[3], r[4]) )

        fTmp = open(out_fname,'w', newline='')
        bNewFile=True
        wri = csv.writer(fTmp, delimiter='\t')
        wri.writerow(aColumns)

        for r in rows:
            wri.writerow(r)

        fTmp.close()
        

        pc("starting argv: {}".format(argv))

        pc("Data written to: {}".format(out_fname))

        pc('.: done :.')
        pc('.')

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        sTB = '\n'.join(traceback.format_tb(exc_traceback))
        pc("Fatal exception: {}\n - msg: {}\n stack: {}".format(exc_type, exc_value, sTB))


if __name__ == '__main__':
    main(sys.argv[1:])
