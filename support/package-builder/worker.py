import os
import sys
import requests
import time
from PackageBuilder import PackageBuilder
from constants import constants

PORT = '80'
def getNextPkgToBuild(MasterIP):
    masterGetPkgApi = 'http://' + MasterIP + ':' + PORT + '/package/'
    package = None
    try:
        response = requests.get(masterGetPkgApi)
    except requests.exceptions.RequestException as e:
        print("Exception in getting response from server:",e)
        return None
        
    if response.status_code != 200:
        print("No package to build")
        print("Response Status = ",response.status_code)
        return None

    return response.text

def getConstants(MasterIP):
    masterConstantsAPI = 'http://' + MasterIP + ':' + PORT + '/constants/'
    try:
        response = requests.get(masterConstantsAPI)
    except requests.exceptions.RequestException as e:
        print("Exception in getting response from server:",e)
        return None

    if response.status_code == 200:
        return response.json()
    else:
        print("Unable to get constants. response code = ",response.status_code)
        print("exiting")
        sys.exit(1)

def initializeConstants(constant_dict):
    ##TODO: split the path and add it to current path
    constants.specPath = constant_dict['specPath']
    constants.sourcePath = constant_dict['sourcePath']
    constants.rpmPath =  constant_dict['rpmPath']
    constants.sourceRpmPath = constant_dict['sourceRpmPath']
    constants.topDirPath = constant_dict['topDirPath']
    constants.logPath = constant_dict['logPath']
    constants.logLevel = constant_dict['logLevel']
    constants.dist = constant_dict['dist']
    constants.buildNumber = constant_dict['buildNumber']
    constants.prevPublishRPMRepo = constant_dict['prevPublishRPMRepo']
    constants.prevPublishXRPMRepo = constant_dict['prevPublishXRPMRepo']
    constants.buildRootPath = constant_dict['buildRootPath']
    constants.pullsourcesURL = constant_dict['pullsourcesURL']
    constants.extrasourcesURLs = constant_dict['extrasourcesURLs']
    constants.buildPatch = constant_dict['buildPatch']
    constants.inputRPMSPath = constant_dict['inputRPMSPath']
    constants.rpmCheck = constant_dict['rpmCheck']
    constants.rpmCheckStopOnError = constant_dict['rpmCheckStopOnError']
    constants.rpmCheckStopOnError = constant_dict['publishBuildDependencies']
    constants.packageWeightsPath = constant_dict['packageWeightsPath']
    constants.userDefinedMacros = constant_dict['userDefinedMacros']
    constants.tmpDirPath =  constant_dict['tmpDirPath']
    constants.buildArch = constant_dict['buildArch']
    constants.currentArch = constant_dict['currentArch']

def getDoneList(MasterIP):
    masterDoneListApi = 'http://' + MasterIP + ':' + PORT + '/donelist/'
    try:
        response = requests.get(masterDoneListApi)
    except requests.exceptions.RequestException as e:
        print("Exception in getting response from server: ",e)
        return None
        
    if response.status_code == 200:
        data = response.json()
        return data["packages"]
    else:
        print("Unable to get DoneList, response code = ",response.status_code)
        sys.exit(1)

def getMapPackageToCycle(MasterIP):
    masterMapPackageToCycleApi = 'http://' + MasterIP + ':' + PORT + '/mappackagetocycle/'
    try:
        response = requests.get(masterMapPackageToCycleApi)
    except requests.exceptions.RequestException as e:
        print("Exception in getting response from server: ",e)
        return None

    if response.status_code == 200:
        return response.json()
    else:
        print("Unable to get MapPackageToCycle, response code = ",response.status_code)
        sys.exit(1)

def notifyMaster(MasterIP,package, buildStatus):
    masterBuildStatusApi = 'http://' + MasterIP + ':' + PORT + '/notifybuild/'
    try:
        response = requests.post(masterBuildStatusApi, json = {'package': package, 'status': buildStatus})
    except requests.exceptions.RequestException as e:
        print("Exception in getting response from server: ",e)

    if response.status_code == 200:
       print("master notified")
    else:
       print("Unable to notify master, error code = ",response.status_code,",response = ",response.json)
       sys.exit(1)

def doBuild(package, doneList, mapPackageToCycle):
    pkgBuilder = PackageBuilder(mapPackageToCycle, "chroot")
    status = 0
    try:
        pkgBuilder.build(package, doneList)
    except Exception as e:
        print("Building exception=",e)
        status = -1

    return status

def getMasterDetails():
    MasterIP = None
    try:
        MasterIP =  os.environ['MASTER_SERVICE_SERVICE_HOST']
    except KeyError:
        print("Environment variable does not exist")
    print("MasterIP: ",MasterIP)
    return MasterIP

if __name__ == "__main__":
    print("Getting master details")
    MasterIP = getMasterDetails()
    while True:
        package = getNextPkgToBuild(MasterIP)
        if package is None:
            time.sleep(15)
            continue
        constants_dict = getConstants(MasterIP)
        doneList = getDoneList(MasterIP)
        mapPackageToCycle = getMapPackageToCycle(MasterIP)
        if constants_dict is None or doneList is None or mapPackageToCycle is None:
            time.sleep(15)
            continue
        initializeConstants(constants_dict)
        status = doBuild(package, doneList, mapPackageToCycle)
        notifyMaster(MasterIP, package, status)
