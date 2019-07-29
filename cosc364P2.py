'''-------------------------------------------'''
# ~ Assignment2
'''-------------------------------------------'''
# ~ source node      : Si
# ~ transit node     : Tk
# ~ destination node : Dj
'''-------------------------------------------'''
import subprocess
import time

def generateDemandVolume(S, T, D):
    '''
    hij = 2*i + j   given in assignment
    '''
    everyDemandVolume = []
    for i in range(1, S+1):
        for j in range(1, D+1):
            SD_record = []          #record Source -> different transit -> Destination
            for k in range(1, T+1):
                SD_record.append("x{}{}{}".format(i, k, j))
            everyDemandVolume.append(" + ".join(SD_record) + " = {}".format(2*i + j))
    return everyDemandVolume


def generateSTcapacity(S, T, D):
    '''
    calculate capacity(Cik) between source node Si and transit node Tk
    '''
    everySTcap = []
    for i in range(1, S+1):
        for k in range(1, T+1):
            ST_record = []          #record Source -> Transit -> different destination
            for j in range(1, D+1):
                ST_record.append("x{}{}{}".format(i, k, j))
            everySTcap.append(" + ".join(ST_record) + " - c{}{} ".format(i, k)  + " <= 0")
    return everySTcap


def generateTDcapacity(S, T, D):
    '''
    calculate capacity(Djk) between transit node Tk and destination node Dj
    '''
    everyTDcap = []
    for j in range(1, D+1):
        for k in range(1, T+1):
            TD_record = []          #record different source -> Transit -> Destination
            for i in range(1, S+1):
                TD_record.append("x{}{}{}".format(i, k, j))
            everyTDcap.append(" + ".join(TD_record) + " - d{}{}".format(k, j) + " <= 0")
    return everyTDcap


def generateBinary(S, T, D):
    '''
    set binary as 1 when path went through, if not set 0
    demand volime split exactly two different paths
    the total number of paths of source node to destination is 2
    so set binary of two paths as 2
    '''
    evertBinary = []
    for i in range(1, S+1):
        for j in range(1, D+1):
            SD_record = []
            for k in range(1, T+1):
                SD_record.append("u{}{}{}".format(i, k, j))
            evertBinary.append(" + ".join(SD_record) + " = 2")
    return evertBinary


def generatePathFlow(S, T, D):
    '''
    Xikj = Uikj x Hij / Nij <=> Nij x Xikj = Hij x Uikj
    Nij = 2   : number of spilt paths
    Hij = 2*i + j both give in assignment
    '''
    everyPathFlow = []
    for i in range(1, S+1):
        for k in range(1, T+1):
            for j in range(1, D+1):
                everyPathFlow.append("{} x{}{}{} - {} u{}{}{} = 0".format(\
                2, i, k, j, 2*i+j, i, k, j))
    return everyPathFlow


def generateTransitLoad(S, T, D):
    '''
    calculate sum of each transit node for all Xijk, which j is constant
    should smaller or equal than Minimize r
    '''
    everyWholeTransit = []
    for k in range(1, T+1):
        everyTransitLoad = []
        for i in range(1, S+1):
            ST_record = []
            for j in range(1, D+1):
                ST_record.append("x{}{}{}".format(i,k,j))
            everyTransitLoad.append(" + ".join(ST_record))
        everyWholeTransit.append(" + ".join(everyTransitLoad) + " - r <= 0")
    return everyWholeTransit


def generateNoneNegativity(S, T, D):
    '''
    Xikj,Cik,Djk cannot be negative (Bounds)
    '''
    everyNoneNegat = ["r >= 0"]
    for i in range(1, S+1):
        for k in range(1, T+1):
            for j in range(1, D+1):
                everyNoneNegat.append("x{}{}{} >= 0".format(i, k, j))   #record all (paths)source -> transit -> different destination:
    everyNoneNegat = list(sorted(set(everyNoneNegat)))
    return everyNoneNegat


def setBinaries(S, T, D):
    '''
    generate Binary as 1
    '''
    everyBiniaries = []
    for i in range(1, S+1):
        for k in range(1, T+1):
            for j in range(1, D+1):
                everyBiniaries.append("u{}{}{}".format(i, k, j))
    return everyBiniaries


def recordText(S, T, D):
    '''record all text lp.file'''
    text = ""

    text += "\n".join(generateDemandVolume(S, T, D))    + "\n"
    text += "\n".join(generateSTcapacity(S, T, D))      + "\n"
    text += "\n".join(generateTDcapacity(S, T, D))      + "\n"
    text += "\n".join(generateBinary(S, T, D))          + "\n"
    text += "\n".join(generatePathFlow(S, T, D))        + "\n"
    text += "\n".join(generateTransitLoad(S, T, D))     + "\n"
    text += "Bounds\n" + \
            "\n".join(generateNoneNegativity(S, T, D))  + "\n"
    text += "Binary\n" + \
            "\n".join(setBinaries(S, T, D))             + "\n"

    text += "END"
    return text


def generateLPfile(S, T, D, text):
    '''
    generate LP files
    '''
    fileName = "{}{}{}.lp".format(S, T, D)
    f = open(fileName,"w")
    lpText = \
    "Minimize \nr \nSubject to \n{}".format(text)
    f.write(lpText)
    f.close


########################################################
# ~ generate lp file done
########################################################
# ~ CPLEX testing below
########################################################

def HightestCapacity(variable_dict):
    '''
    generate Hightest Capacity with value and keys
    '''
    HightestValue = max(variable_dict.values())
    HightestKeys = [k for k, v in variable_dict.items() if v == HightestValue]
    return HightestKeys, HightestValue


def NonZeroCapacities(variable_dict):
    '''
    generate number of link with NON-ZERO capacities
    '''
    non_zeroCapacitiesCount = 0
    for k , v in variable_dict.items():
        if  "c" in k or "d" in k:       # count number of NON-ZERO capacities
            non_zeroCapacitiesCount += 1
    return non_zeroCapacitiesCount


def CalcuTransitLoad(variable_dict, T):
    '''
    calculate the load on the transit nodes
    '''
    linkDict = []
    numTransitNode = {}


    for k , v in variable_dict.items():
        if "x" in k:                    # collect all x{}{}{} variable
            linkDict += [(k, v)]

    for n in range(1, T+1):             #create a Transit Node DICT to collect link with same Transit Node
        numTransitNode[n] = 0
    for i in linkDict:                  #collect processing
        numTransitNode[int(i[0][2])] += float(i[1])

    return numTransitNode



def CPLEX_run(S,T,D):
    '''
    RUN CPLEX and analysing lp files
    '''

    fileName = "{}{}{}.lp".format(S, T, D)
    command = [
        "/home/cosc/student/yzh254/Desktop/COSC364/My364/unlimited_edition/cplex/bin/x86-64_linux/cplex",
        "-c",
        "read /home/cosc/student/yzh254/Desktop/COSC364/My364/" +
        fileName,
        "optimize",
        'display solution variables -']         #  Address in School


    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    text = p.stdout.read().splitlines()

    executiontTime = ""
    for x in range(len(text)):                         # cut all text from ternimal start-------------------------
        if ("Solution time" in text[x]):               # looking for executiont time
            executiontTime = text[x].replace(" ","")\
                                    .replace("Iterations","")\
                                    .split("=")[1]

        if text[x] == "CPLEX> Incumbent solution":      #looking for information we want
            unsort_text = text[x+3:]
    for y in range(len(unsort_text)):
        if "u" in unsort_text[y]:                       #looking for last element and delete all irrelevant
            variable_text = unsort_text[:y+1]           #cut cut all text from ternimal end  -----------

    variable_dict = {}                                  #put all elements into dict  =>   {}{}{} : number
    for z in variable_text:
        z = z.split()[0], float(z.split()[1])
        z = dict([z])
        variable_dict = dict(variable_dict.items() + z.items())


    print('''
|----------------------------------------------------------------------------|
File : {}{}{}.lp

Execution time :            {}

Hightest capacity value:    {}

Hightest capacity link(s):  {}

Number of link with Non-zero capacities:    {}

Transit nodes load :        {}
|----------------------------------------------------------------------------|
    '''.format(
    S, T, D,
    executiontTime,                             # Execution time
    HightestCapacity(variable_dict)[1],         # HightestCapacity with value
    HightestCapacity(variable_dict)[0],         # HightestCapacity with links
    NonZeroCapacities(variable_dict),           # Non-Zero Capacities links
    CalcuTransitLoad(variable_dict, T)))        # Load on the transit nodes



def main():
    S,T,D = 3,2,4            # number of Source nodes/ Transit nodes / Destination nodes
    generateLPfile(S, T, D, recordText(S, T, D))
    CPLEX_run(S,T,D)


    T = 3                    #testing all config
    while T <= 8:
        S, T, D = 9, T, 9
        generateLPfile(S, T, D, recordText(S, T, D))
        CPLEX_run(S,T,D)
        T+=1


if __name__ == '__main__':
    main()
