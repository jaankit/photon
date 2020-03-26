import flask
import logging
from Scheduler import Scheduler
from constants import constants
app = flask.Flask(__name__)
mapPackageToCycle = {}
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)
def buildCompleted():
    if Scheduler.isAllPackagesBuilt() and not Scheduler.isAnyPackagesCurrentlyBuilding():
        return True
    return False

def shutdownServer():
        print("Shutting down server......")
        stopServer = flask.request.environ.get('werkzeug.server.shutdown')
        if stopServer is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        stopServer()

@app.route('/package/', methods=['GET'])
def getNextPkgToBuild():
    pkg = Scheduler.getNextPackageToBuild()
    if not pkg:
        return '', 204
    print("Scheduling package",pkg)
    return pkg

@app.route('/notifybuild/', methods=['POST'])
def notifyPackageBuildCompleted():
    if flask.request.json['status'] == 0:
        print("Build Success for ",flask.request.json['package'])
        Scheduler.notifyPackageBuildCompleted(flask.request.json['package'])
    elif flask.request.json['status'] == -1:
        print("Build failed for ",flask.request.json['package'])
        Scheduler.notifyPackageBuildFailed(flask.request.json['package'])
    else:
        return {'message', 'wrong status'},501
    if buildCompleted():
        print("Package build completed...")
        shutdownServer()
    return {'message': 'master notified successfully'},200

@app.route('/donelist/', methods=['GET'])
def getDoneList():
    doneList = Scheduler.getDoneList()
    return flask.jsonify(packages=doneList)


@app.route('/mappackagetocycle/', methods=['GET'])
def getMapPackageToCycle():
    return mapPackageToCycle

@app.route('/constants/', methods=['GET'])
def getConstants():
    ##pass only those consranrs variable that are required by package builder
    constant_dict = {}
    constant_dict['specPath'] = constants.specPath
    constant_dict['sourcePath'] = constants.sourcePath
    constant_dict['rpmPath'] = constants.rpmPath
    constant_dict['sourceRpmPath'] = constants.sourceRpmPath
    constant_dict['topDirPath'] = constants.topDirPath
    constant_dict['logPath'] = constants.logPath
    constant_dict['logLevel'] = constants.logLevel
    constant_dict['dist'] = constants.dist
    constant_dict['buildNumber'] = constants.buildNumber
    constant_dict['releaseVersion'] = constants.releaseVersion
    constant_dict['prevPublishRPMRepo'] = constants.prevPublishRPMRepo
    constant_dict['prevPublishXRPMRepo'] = constants.prevPublishXRPMRepo
    constant_dict['buildRootPath'] = constants.buildRootPath
    constant_dict['pullsourcesURL'] = constants.pullsourcesURL
    constant_dict['extrasourcesURLs'] = constants.extrasourcesURLs
    constant_dict['buildPatch'] = constants.buildPatch
    constant_dict['inputRPMSPath'] = constants.inputRPMSPath
    constant_dict['rpmCheck'] = constants.rpmCheck
    constant_dict['rpmCheckStopOnError'] = constants.rpmCheckStopOnError
    constant_dict['publishBuildDependencies'] = constants.publishBuildDependencies
    constant_dict['packageWeightsPath'] = constants.packageWeightsPath
    constant_dict['userDefinedMacros'] = constants.userDefinedMacros
    constant_dict['katBuild'] = constants.katBuild
    constant_dict['tmpDirPath'] = constants.tmpDirPath
    constant_dict['buildArch'] = constants.buildArch
    constant_dict['currentArch'] = constants.currentArch

    return constant_dict


def startServer():
    if buildCompleted():
        return
    print("Starting Server ...")
    app.run(host='0.0.0.0', port='80', debug=True, use_reloader=False)
