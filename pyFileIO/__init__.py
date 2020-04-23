from .util import isSemVerTuple, futureVersion

appVersion = None

class FileIO():
    def __init__(self):
        self.appVersion = None
        self.fileTypes = []
        self.migrations = {}

    def setAppVersion(self, version):
        """Sets the internal version used as the end point for migrations"""
        self.appVersion = version

    def getAppVersion(self):
        if self.appVersion is None:
            raise ValueError('App version not set')
        return self.appVersion

    def registerFileType(self, name):
        if name in self.fileTypes:
            raise ValueError('File type {} already exists'.format(name))
        self.fileTypes.append(name)
        self.migrations[name] = {}

    def registerMigration(self, fileType, fromVer, toVer, func):
        if fileType not in self.fileTypes:
            raise TypeError('File type "{}" is not one of the known file types ({})'.format(fileType, self.fileTypes))
        if not isSemVerTuple(fromVer):
            raise TypeError('Start version is not a semantic version tuple: {}'.format(fromVer))
        if not isSemVerTuple(toVer):
            raise TypeError('End version is not a semantic version tuple: {}'.format(toVer))
        if fromVer == toVer:
            raise ValueError('Start version and end version equal')
        if not futureVersion(toVer, fromVer):
            raise ValueError('End version {} must be newer than start version {}'.format(toVer, fromVer))
        self.migrations[fileType][fromVer] = {
            'to': toVer,
            'function': func
        }

    def migrateData(self, fileType, fromVer, toVer, data):
        currentVersion = fromVer
        migrations = self.migrations[fileType]
        while currentVersion != toVer:
            if currentVersion not in migrations:
                raise ValueError('No migrations from {}'.format(currentVersion))
            func = migrations[currentVersion]['function']
            try:
                data = func(data)
            except Exception as err:
                raise Exception('Error upgrading data from {} to {}: {}'.format(currentVersion,
                                                                                migrations[currentVersion]['to'],
                                                                                err))
            currentVersion = migrations[currentVersion]['to']
        return data

fileIO = FileIO()
