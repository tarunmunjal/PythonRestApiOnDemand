import csv,argparse,re,os,sys
from pathlib import Path

script_arg_parser = argparse.ArgumentParser(description="script to create python flask rest api with mysql backend.")
script_arg_parser.add_argument("--csvfilepath","-in",required=True,help="Path to csv file that contains the needed information.")
script_arg_parser.add_argument("--outfilepath","-out",required=True,help="Full path where output file will be saved. Any existing file will be overwritten.")
all_script_args = script_arg_parser.parse_args()

baseapptop = '''import argparse, os
from werkzeug.exceptions import BadRequest
from flask import Flask, request, Response, json, jsonify
from flask_restful import Resource, Api, reqparse
from flaskext.mysql import MySQL
# This creates the arguments for the application itself.
parserParams = argparse.ArgumentParser()
# By default application will use all ips available on default port 5000. unless specified. 
# IP and Port arguments are optional
parserParams.add_argument("--appIP","-aip",help="IP for the application endpoint. Default is 0.0.0.0",required=False,default='0.0.0.0')
parserParams.add_argument("--appPort","-ap",help="Port for application endpoint. Default is 5000.",required=False,type=int,default=5000)
# Need to know the information about MySQL server. DB Server IP or Hostname, username, password, database name.
# These parameters are mandatory
parserParams.add_argument("--dbserver","-dbs",help="Mysql datbase server IP/Hostname.",required=True)
parserParams.add_argument("--dbuser","-dbu",help="username for mysql server connection.",required=True)
parserParams.add_argument("--dbpassword","-dbp",help="password for mysql server connection.",required=True)
parserParams.add_argument("--dbname","-dbn",help="mysql database name.",required=True)

# Parse the arguments passed
allParams = parserParams.parse_args()
# Create an instance of Flask 
app = Flask(__name__)
# Create an instance of MySQL 
mysql = MySQL()
# Add MySQL configuration to app instance
app.config['MYSQL_DATABASE_HOST'] = allParams.dbserver
app.config['MYSQL_DATABASE_USER'] = allParams.dbuser
app.config['MYSQL_DATABASE_PASSWORD'] = allParams.dbpassword
app.config['MYSQL_DATABASE_DATABASE'] = allParams.dbname
mysql.init_app(app)
'''

baseappbottom = '''
if __name__ == '__main__':
\tapp.run(host=allParams.appIP,port=allParams.appPort)
'''

def check_route_for_arguments(route_string):
    pattern = re.compile("<")
    if pattern.findall(csv['route']):
        routeparam = csv['route'].split("/")[-1]
        pattern_param = re.compile(":")
        if pattern_param.findall(routeparam):
            routeparam = (routeparam.split(":")[-1]).strip(">")
        return routeparam

def get_route_params(route):
    pattern = re.compile("<")
    routes_params = route.split("/")
    route_paramet = map(lambda route_param: (route_param.split(":")[-1]).replace(">","").replace("<",""), [route_param for route_param in routes_params if pattern.findall(route_param)])
    route_param_to_add = ','.join(route_paramet)             
    return route_param_to_add


def create_list_from_param_string(stored_proc_params):
    if type(stored_proc_params) == str:
        list_params = stored_proc_params.split(",")
        return list_params
    elif type(stored_proc_params) == list:
        return stored_proc_params



def add_params_to_routes(route_params):
    param_output_list = []
    if route_params != "":
        param_output_list.append("\t\tparser = reqparse.RequestParser()")
        route_param_list = route_params.split(",")
        for route_param in route_param_list:
            param_output_list.append("\t\tparser.add_argument('{}',location=['headers','args','form','values','params','json'])".format(route_param))
        param_output_list.append("\t\targs = parser.parse_args()")
    return param_output_list

def add_mysql_connect_block(spname,route_params,endpoint_sql_param):
    mysql_block_list = '''\t\tconn = mysql.connect()
\t\tcursor = conn.cursor()
\t\tcursor.callproc(ReplaceWithSPName,(ReplaceWithParams))
\t\tqueryResult = [ dict(line) for line in [zip([ column[0] for column in cursor.description], row) for row in cursor.fetchall()] ]
\t\tconn.commit()
\t\treturn json.dumps({'status_code':'200','results':queryResult})'''
    if route_params or endpoint_sql_param:
        mysql_param_string = route_params
        if endpoint_sql_param:
            mysql_block_list = mysql_block_list.replace("ReplaceWithParams",endpoint_sql_param+",ReplaceWithParams")
        if route_params:
            for route_param in route_params.split(","):
                mysql_param_string = mysql_param_string.replace(route_param,"args['{}']".format(route_param))
        else:
            mysql_block_list = mysql_block_list.replace(",ReplaceWithParams","")
    return ((mysql_block_list.replace("ReplaceWithSPName","'{}'".format(spname))).replace('ReplaceWithParams',mysql_param_string)).rstrip()

def create_routes(route,spname,route_params,call_method):
    def_name = "tm"+(((route.replace("/","_")).replace("<","")).replace(">","")).replace(":","_")
    pattern = re.compile("<")
    route_param_added = None
    if pattern.findall(route):
        route_param_added = get_route_params(route)
        full_def_string = "def "+def_name+"_"+call_method + "({}):".format(route_param_added)
    else:
        full_def_string = "def "+def_name+"_"+call_method + "():"
    full_route_def_block = []
    full_route_def_block.append('@app.route("{}", methods=[\'{}\'])\n'.format(route,call_method))
    full_route_def_block.append(full_def_string+"\n")
    full_route_def_block.append("\ttry:\n")
    for plist in add_params_to_routes(route_params):
        full_route_def_block.append(plist+"\n")
    full_route_def_block.append(add_mysql_connect_block(spname,route_params,route_param_added)+"\n")
    full_route_def_block.append("\texcept Exception as my_exception:\n")
    full_route_def_block.append("\t\treturn str(my_exception), 400\n")
    return full_route_def_block



csvfilepath = all_script_args.csvfilepath
outfilepath = all_script_args.outfilepath
### check if destination file path exists.
out_file_path, out_file_name = os.path.split(outfilepath)
if os.path.exists(outfilepath):
    choice = (input("Warning: File {} in path {} exists. Proceed and overwrite existing file? y/n :".format(out_file_name,out_file_path))).lower()
    if choice == "n":
        sys.exit(1)
else:
    if not os.path.exists(out_file_path):
        print("Path {} doesn't exist will try to recursively create path".format(out_file_path))
        try:
            print("Creating folder".format(out_file_path))
            os.makedirs(out_file_path)
        except Exception as my_exception:
            sys.exit(my_exception)

print("Starting process")
## Start process only if csv file exists.
if os.path.exists(csvfilepath):
    routecsv = open(csvfilepath,"r")    
    ch = [ch for ch in ((routecsv.readline().replace('"','')).strip()).split(",") if ch in ['route','spname','spparams','method']]
    if len(ch) != 4:
        raise Exception("headers cannot be validaed")
    routecsv.seek(0)
    csvreader = csv.DictReader(routecsv, delimiter=",")
    with open(outfilepath,"w+") as writeapi:
        writeapi.write(baseapptop)
        for csv in csvreader:
            stored_proc_param_list = csv["spparams"]
            for plist in create_routes(csv['route'],csv['spname'],stored_proc_param_list,csv['method']):
                writeapi.write(plist)
            writeapi.write("\n\n\n")
        writeapi.write(baseappbottom)
    routecsv.close()
else:
    print("raising exception")
    raise Exception("csvfile not found")