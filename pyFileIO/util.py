def isSemVerTuple(value):
    """Returns true if "value" is a semantic version tuple"""
    return type(value) is tuple and len(value) == 3 and all([type(i) is int for i in value])

def futureVersion(verA, verB):
    """Returns true if version A is newer than version B"""
    if not isSemVerTuple(verA):
        raise TypeError('Argument 0 ({}) is not a semantic version tuple'.format(verA))
    if not isSemVerTuple(verB):
        raise TypeError('Argument 1 ({}) is not a semantic version tuple'.format(verB))
    major = verA[0] > verB[0]
    minor = verA[0] == verB[0] and verA[1] > verB[1]
    fix = verA[0] == verB[0] and verA[1] == verB[1] and verA[2] > verB[2]
    return major or minor or fix
