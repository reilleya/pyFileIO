import yaml

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

    def save(self, fileType, data, path):
        if fileType not in self.fileTypes:
            raise ValueError('Unknown file type: {}'.format(fileType))

        output = {
            'version': self.getAppVersion(),
            'type': fileType,
            'data': data
        }

        with open(path, 'w') as saveLocation:
            yaml.dump(output, saveLocation)

    def load(self, fileType, path):
        if fileType not in self.fileTypes:
            raise ValueError('Unknown file type: {}'.format(fileType))

        with open(path, 'r') as readLocation:
            fileData = yaml.full_load(readLocation)

            if 'data' not in fileData or 'type' not in fileData or 'version' not in fileData:
                raise ValueError('File did not contain the required fields')

            if fileData['type'] != fileType:
                raise TypeError('Loaded data type did not match expected type.')

            if fileData['version'] == self.getAppVersion():
                return fileData['data'] # If the data is from the current version it doesn't need migration

            # If the data is from a future version, it can't be loaded
            if futureVersion(fileData['version'], self.getAppVersion()):
                new = '.'.join(str(num) for num in fileData['version'])
                old = '.'.join(str(num) for num in appVersion)
                raise ValueError("Data is from a future version (" + new + " vs " + old + ") and can't be loaded.")

            # Otherwise it is from a past version and will be migrated
            return self.migrateData(fileType, fileData['version'], self.getAppVersion(), fileData['data'])


fileIO = FileIO()
