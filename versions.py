import requests
import getpass
from openpyxl import Workbook
import time

token = getpass.getpass() 
    
def form_api_headers():
    global token
    payload = {'Accept' : 'application/json' , 'Content-Type' : 'application/json' , 'Authorization' : 'Token '+token}
    return payload

def check_token():
    """Validates a given API token."""
    r = requests.get('https://network.pivotal.io/api/v2/authentication', headers=form_api_headers())
    print(r.status_code)

def get_product_list():
    """Returns a list of dictionaries of all products from the API."""
    r = requests.get('https://network.pivotal.io/api/v2/products', headers=form_api_headers())
    datadict = r.json()
    plist = datadict.get('products')
    return plist

def get_product_ids():
    """Returns a list of all product IDs."""
    plist = get_product_list()
    idlist = []
    for i in range(len(plist)):
        idlist.append(int(plist[i]['id']))
    return sorted(idlist)

def get_product_release_dict(slug):
    """Makes a dictionary of all releases for a given product slug where the keys are release IDs and the values are version numbers."""
    r = requests.get('https://network.pivotal.io/api/v2/products/'+str(slug)+'/releases', headers=form_api_headers())
    datadict = r.json()
    rlist = datadict.get('releases')
    cleandict = {}
    for i in range(len(rlist)):
        cleandict[rlist[i]['id']] = rlist[i]['version']
    return cleandict

def get_clean_release_dependencies(product_id, release_id):
    """Makes a dictionary of all release dependencies for a given product release where the keys are the dependency release IDs and the values are a tuple of the dependency product name and version number."""
    r = requests.get('https://network.pivotal.io/api/v2/products/'+str(product_id)+'/releases/'+str(release_id)+'/dependencies', headers=form_api_headers())
    datadict = r.json()
    dlist = datadict.get('dependencies')
    cleandict = {}
    for i in range(len(dlist)):
        cleandict[dlist[i]['release']['id']] = (dlist[i]['release']['product']['name'],dlist[i]['release']['version'])
    return cleandict




class PivProduct:
    
    def __init__(self, id, plist):
        self.id = id
        self.productname = self.get_product_name(plist)
        self.productslug = self.get_product_slug(plist)
        self.releases = []
    
    def get_product_name(self, plist):
        """Returns a product name for a given ID"""
        cleandict = {}
        for i in range(len(plist)):
            cleandict[plist[i]['id']] = plist[i]['name']
        return cleandict[self.id]
        
    def get_product_slug(self, plist):
        """Returns a product slug for a given ID"""
        cleandict = {}
        for i in range(len(plist)):
            cleandict[plist[i]['id']] = plist[i]['slug']
        return cleandict[self.id]
        
    def __str__(self):
        return str(self.id)+"_"+self.productname
        

class PivRelease:

    def __init__(self, id, rdict):
        self.id = id
        self.version = self.get_version(rdict)
        self.dependencies = []
        
    def get_version(self, rdict):
        return rdict[self.id]

class PivDependency:

    def __init__(self, id, ddict):
        self.id = id
        self.version = self.get_dep_version(ddict)
        self.productname = self.get_dep_name(ddict)
    
    def get_dep_version(self, ddict):
        return ddict[self.id][1]
        
    def get_dep_name(self, ddict):
        return ddict[self.id][0]


timestart = time.time()
check_token()                   #200 is good
plist = get_product_list()
ids = get_product_ids()
pivproductslist = []
sheetnamelist = []
sheetdict = {}

wb = Workbook(write_only=True)

count = 0
for item in ids:
    pivproductslist.append(PivProduct(item, plist))
    count += 1

count2 = 0
for item in pivproductslist:                                        #For every product object
    sheetdict[item.id] = wb.create_sheet(item.productname[:30])     #Add a pair to a dictionary where the key is the product ID and the value is an Excel sheet with the product name
    sheetdict[item.id].append(["Release ID", "Release Number", "Dependency Release ID", "Dependency Product Name", "Dependency Version Number"]) #Add a header to the excel sheet
    
    rdict = get_product_release_dict(item.productslug)
    print(str(item)+" has "+str(len(rdict))+" releases.")
    for key in rdict:                           #For every release for the product
        r = PivRelease(key, rdict)              #Make a release object
        item.releases.append(r)                 #Add the release object to the product's release list
        rowprefix = [r.id, r.version] #Make a prefix for the dependency rows
        ddict = get_clean_release_dependencies(item.id, r.id) #Get the release's dependencies
        for dkey in ddict:                  #For each of the dependencies
            d = PivDependency(dkey, ddict)  #Make a dependency object
            r.dependencies.append(d)      #Add it to the release's dependency list
            rowsuffix = [d.id, d.productname, d.version] #Make the spreadsheet row suffix
            sheetdict[item.id].append(rowprefix + rowsuffix) #Add the spreadsheet row

wb.save('myfile.xlsx')
timefinish = time.time()

print("Total elapsed time is "+str(timefinish-timestart)+" seconds.")

