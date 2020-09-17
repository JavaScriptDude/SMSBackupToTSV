import os
from datetime import datetime
from pprint import pformat as pf


def exit(s=None, exitCode=1):
    pc('exit() called from: {}'.format(getCaller()))
    if not s is None:
        pc('Message: {}'.format(s))
    pc('exiting program ~')
    sys.stdout.flush()
    sys.stderr.flush()
    sys.exit(exitCode)


def pc(*args):
    a = []; i=0
    for v in args:
        a.append( ( v if i == 0 or isinstance(v, (int, float, complex, str)) else pf(v, indent=1, width=80, depth=2) ) )
        i = i + 1
    print(a[0] if i == 1 else a[0].format(*a[1:]))


def parseDate(sDate):
    sDate = sDate.replace('a.m.', 'AM').replace('p.m.', 'PM').replace('.', '')
    d = datetime.strptime(sDate, "%b %d, %Y %H:%M:%S %p")
    return [d.year, d.month, d.day, d.strftime('%H:%M:%S')]


def fixPhone(sPhone):
    sPhone = sPhone.strip()
    if len(sPhone) == 0 or sPhone == "unavailable" or sPhone.find('@') > -1: return sPhone
    if sPhone.find("~") > -1:
        a = sPhone.split('~')
        return ', '.join(list(map(lambda s: fixPhone(s), sPhone.split('~'))))
    if not sPhone[0] == "+" and not sPhone[0] == '1': 
        s = '1' + sPhone.replace('-', '')
    else:
        s = sPhone.replace('+', '').replace('-', '')
    if len(s) < 8: return sPhone
    # pc("s = {}", s)
    return format(int(s[:-1]), ",").replace(",", "-") + s[-1]


def loadArgs(argv, alias):
    if len(argv) == 1:
        sFile = argv[0]
    else:
        _exit("Please pass {} xml file name to parser".format(alias))
    if not os.path.isfile(sFile):
        _exit("'{}' xml file not found: {}".format(alias, sFile))
    return (sFile)


def getMachineDTMS(dt:datetime=None):
    dt = datetime.now() if dt is None else dt
    return dt.strftime("%y%m%d-%H%M%S.%f")[:-3]


def aget(alias, obj, sKey, req=True, toint=False):
    v = None; bFail = False

    try:
        v = obj.get(sKey)
    except:
        pass

    if v is None:
        if not req: return ""
        raise AgetException('Missing key {} from {}'.format(sKey, alias))

    if toint: return int(v)

    return v

def dump(o, showType: bool = True):
    if o is None: return None
    if isinstance(o, Xml_Element):
        v = xml_et_tostring(o).decode()
    else:
        v = pf(o)
    return ('{} {}'.format(type(o), v) if showType else v)


class AgetException(BaseException):
    pass


class QNull():
    pass
