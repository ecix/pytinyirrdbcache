from flask import Flask
from flask import Response

import json

import inc
from inc.whoisDatabases import WhoisDatabaseContainer

whoisDatabaseContainer = WhoisDatabaseContainer()

app = Flask(__name__)

@app.route("/")
def displayAPI():
    description = ""
    description += "<div style=\"margin-top: 20px;margin-bottom: 20px;\">an optimized whois cache for building bird configs</div>"
    description += ""
    description += "<div><a href=\"/getDatabaseInfo\">/getDatabaseInfo</a>:"
    description += "        <div style=\"margin-left:50px\">get information about the cached whois databases</div></div>"
    description += "<div><a href=\"/getPrefixInformation/ripe/AS-CHAOS/v4\">/getPrefixInformation/&lt;string:databaseName&gt;/&lt;string:macro&gt;/&lt;string:ipVersion&gt;</a>:"
    description += "        <div style=\"margin-left:50px\">fetches the prefix information like tinyirrdbcache does</div></div>"
    description += "<div><a href=\"/resolveMacro/ripe/AS-CHAOS\">/resolveMacro/&lt;string:databaseName&gt;/&lt;string:macro&gt;</a>:"
    description += "        <div style=\"margin-left:50px\">resolve a macro to ASNs</div></div>"
    description += "<div><a href=\"/resolveASN/ripe/AS44194/v4\">/resolveASN/&lt;string:databaseName&gt;/&lt;string:asn&gt;/&lt;string:ipversion&gt;</a>:"
    description += "        <div style=\"margin-left:50px\">resolve an ASN to prefixes</div></div>"
    description += "<div><a href=\"/resolveASNs/ripe/v6\">/resolveASNs/&lt;string:databaseName&gt;/&lt;string:ipversion&gt;<a>:"
    description += "        <div style=\"margin-left:50px\">resolve all ASNs to prefixes</div></div>"
    description += "<div><a href=\"/rebuildDatabase\">/rebuildDatabase</a>:"
    description += "        <div style=\"margin-left:50px\">rebuilds the database from scratch</div></div>"
    description += "<div><a href=\"/updateDatabase\">/updateDatabase</a>:"
    description += "        <div style=\"margin-left:50px\">update the database from the whois database</div></div>"
    description += "<div><a href=\"/stats\">/stats</a>:"
    description += "        <div style=\"margin-left:50px\">get statistics about the database</div></div>"

    return description

@app.route("/rebuildDatabase")
def rebuildDatabaseRequest():
    whoisDatabaseContainer.rebuild()
    return "done"

@app.route("/updateDatabase")
def updateDatabaseRequest():
    whoisDatabaseContainer.update()
    return "done"

@app.route("/getPrefixInformation/<string:databaseName>/<string:macro>/<string:ipVersion>")
def retrievePrefixInformation(databaseName, macro, ipVersion):
    database = whoisDatabaseContainer.getDatabase(databaseName)

    result = database.fetch( macro, ipVersion)

    result["prefixes"] = list(result["prefixes"])
    result["macros"] = list(result["macros"])

    data = json.dumps(result)

    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route("/resolveMacro/<string:databaseName>/<string:macro>")
def resolveMacro(databaseName, macro):
    database = whoisDatabaseContainer.getDatabase(databaseName)

    result = database.resolveMacro(macro)

    result["macros"] = list(result["macros"])
    result["asns"] = list(result["asns"])

    data = json.dumps(result)

    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route("/resolveASN/<string:databaseName>/<string:asn>/<string:ipVersion>")
def resolveASN(databaseName, asn, ipVersion):
    database = whoisDatabaseContainer.getDatabase(databaseName)

    result = database.resolveASN(asn, ipVersion)

    data = json.dumps(result)

    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route("/resolveASNs/<string:databaseName>/<string:ipVersion>")
def resolveASNs(databaseName, ipVersion):
    database = whoisDatabaseContainer.getDatabase(databaseName)

    result = database.resolveASNs( ipVersion )
    result = dict([(k, list(v)) for (k, v) in result.iteritems()])

    data = json.dumps(result)

    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route("/getDatabaseInfo")
def getDatabaseInformation():
    data = json.dumps(whoisDatabaseContainer.getInfo())

    resp = Response(data, status=200, mimetype='application/json')
    return resp

@app.route("/stats")
def getStatsRequest():
    import resource

    memusage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    memusage += resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss

    stats = { "memoryUsage":memusage, "whoisDatabases":whoisDatabaseContainer.getDatabaseCount() }

    data = json.dumps(stats)

    resp = Response(data, status=200, mimetype='application/json')

    return resp

if __name__ == "__main__":
    #app.run( port=8087 )
    app.run( debug=True, port=8087 )
