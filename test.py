errors = []
toTest = ["AS-KORNET","ASTest","AS-CHAOS"]
toTest = ["AS-ALENTUSCA-CUSTOMERS","AS-8167-BGP-CUSTOMERS","AS-CHAOS"]
tested = []

def test_getPrefixInformation(dbname, macro, ipVersion):
    if macro in tested:
        return

    import requests
    print("fetching first file")
    r = requests.get('http://localhost:8086/'+dbname+'/'+macro+'/'+ipVersion)
    vals_8086 = r.json()

    print("fetching second file")
    r = requests.get('http://localhost:8087/getPrefixInformation/'+dbname+'/'+macro+'/'+ipVersion)
    vals_8087 = r.json()

    if not vals_8086["prefixCount"] == vals_8087["prefixCount"]:
        print("prefix count differs: ")
        print("8086: "+str(vals_8086["prefixCount"]))
        print("8087: "+str(vals_8087["prefixCount"]))
    else:
        print("prefixCount is identical: "+str(vals_8086["prefixCount"]))

    if not (len(set(vals_8086["prefixes"])) == len(set(vals_8087["prefixes"]))):
        errors.append("""
unique prefix count differs for """+dbname+""" """+macro+""" """+ipVersion+""" 
8086: """+str(len(set(vals_8086["prefixes"])))+"""
8087: """+str(len(set(vals_8087["prefixes"])))+"""
""")
        print(errors[-1])
    else:
        print("unique prefixCount is identical: "+str(len(set(vals_8086["prefixes"]))))

    found = False
    for val in vals_8086["prefixes"]:
        if not val in vals_8087["prefixes"]:
            if not found:
                errors.append("""
prefixes in 8086 but not in 8087: 
""")
                print(errors[-1])
            found = True
            errors.append((val)+"\n")
            print(errors[-1])
    if not found:
        print("all prefixes in 8086 are in 8087")

    found = False
    for val in vals_8087["prefixes"]:
        if not val in vals_8086["prefixes"]:
            if not found:
                errors.append("""
prefixes in 8087 but not in 8086: 
""")
                print(errors[-1])
            found = True
            errors.append((val)+"\n")
            print(errors[-1])
    if not found:
        print("all prefixes in 8087 are in 8086")

    tested.append(macro)
    print(toTest)
    toTest.extend(vals_8087["macros"])
    toTest.extend(vals_8086["macros"])
    print(toTest)

while True:
    macro = toTest.pop()
    print("testing:")
    print(macro)
    test_getPrefixInformation("radb",macro,"v4")
    if len(toTest) == 0:
        break

print("errors: ")
print(errors)
