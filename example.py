import argparse, os
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
@app.route("/createauthor", methods=['post'])
def tm_createauthor_post():
	try:
		parser = reqparse.RequestParser()
		parser.add_argument('firstname',location=['headers','args','form','values','params','json'])
		parser.add_argument('lastname',location=['headers','args','form','values','params','json'])
		parser.add_argument('email',location=['headers','args','form','values','params','json'])
		parser.add_argument('address1',location=['headers','args','form','values','params','json'])
		parser.add_argument('address2',location=['headers','args','form','values','params','json'])
		parser.add_argument('zipcode',location=['headers','args','form','values','params','json'])
		parser.add_argument('phone',location=['headers','args','form','values','params','json'])
		args = parser.parse_args()
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('spCreateAuthor',(args['firstname'],args['lastname'],args['email'],args['address1'],args['address2'],args['zipcode'],args['phone']))
		queryResult = [ dict(line) for line in [zip([ column[0] for column in cursor.description], row) for row in cursor.fetchall()] ]
		conn.commit()
		return json.dumps({'status_code':'200','results':queryResult})
	except Exception as my_exception:
		return str(my_exception), 400



@app.route("/updatebookauthor", methods=['post'])
def tm_updatebookauthor_post():
	try:
		parser = reqparse.RequestParser()
		parser.add_argument('bookname',location=['headers','args','form','values','params','json'])
		parser.add_argument('authorid',location=['headers','args','form','values','params','json'])
		args = parser.parse_args()
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('spUpdateBookAuthor',(args['bookname'],args['authorid']))
		queryResult = [ dict(line) for line in [zip([ column[0] for column in cursor.description], row) for row in cursor.fetchall()] ]
		conn.commit()
		return json.dumps({'status_code':'200','results':queryResult})
	except Exception as my_exception:
		return str(my_exception), 400



@app.route("/updatebookname", methods=['post'])
def tm_updatebookname_post():
	try:
		parser = reqparse.RequestParser()
		parser.add_argument('bookid',location=['headers','args','form','values','params','json'])
		parser.add_argument('bookname',location=['headers','args','form','values','params','json'])
		args = parser.parse_args()
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('spUpdateBookName',(args['bookid'],args['bookname']))
		queryResult = [ dict(line) for line in [zip([ column[0] for column in cursor.description], row) for row in cursor.fetchall()] ]
		conn.commit()
		return json.dumps({'status_code':'200','results':queryResult})
	except Exception as my_exception:
		return str(my_exception), 400



@app.route("/author/<authorid>", methods=['get'])
def tm_author_authorid_get(authorid):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('spGetAuthorBooks',(authorid))
		queryResult = [ dict(line) for line in [zip([ column[0] for column in cursor.description], row) for row in cursor.fetchall()] ]
		conn.commit()
		return json.dumps({'status_code':'200','results':queryResult})
	except Exception as my_exception:
		return str(my_exception), 400



@app.route("/authorinfo", methods=['get'])
def tm_authorinfo_get():
	try:
		parser = reqparse.RequestParser()
		parser.add_argument('authorid',location=['headers','args','form','values','params','json'])
		parser.add_argument('firstname',location=['headers','args','form','values','params','json'])
		parser.add_argument('lastname',location=['headers','args','form','values','params','json'])
		parser.add_argument('email',location=['headers','args','form','values','params','json'])
		args = parser.parse_args()
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('spGetAuthorinfo',(args['authorid'],args['firstname'],args['lastname'],args['email']))
		queryResult = [ dict(line) for line in [zip([ column[0] for column in cursor.description], row) for row in cursor.fetchall()] ]
		conn.commit()
		return json.dumps({'status_code':'200','results':queryResult})
	except Exception as my_exception:
		return str(my_exception), 400



@app.route("/createbook/<authorid>", methods=['post'])
def tm_createbook_authorid_post(authorid):
	try:
		parser = reqparse.RequestParser()
		parser.add_argument('bookname',location=['headers','args','form','values','params','json'])
		args = parser.parse_args()
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('spCreateBook',(authorid,args['bookname']))
		queryResult = [ dict(line) for line in [zip([ column[0] for column in cursor.description], row) for row in cursor.fetchall()] ]
		conn.commit()
		return json.dumps({'status_code':'200','results':queryResult})
	except Exception as my_exception:
		return str(my_exception), 400




if __name__ == '__main__':
	app.run(host=allParams.appIP,port=allParams.appPort)
