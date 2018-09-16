# PythonRestApiOnDemand
This project is to provide a functional restapi.

Below are the requirments:

Backend should be MySQL.

Any calls to backend are made using Stored Procedures.
Stored procedure must be able to handle null values passed to them for optional parameters.
If the route contains variable e.g. /this/test/<string:param1>/<string:param2> param1 and param2 will be the first two params
in for stored procedure call.
Stored procedre call will contain all the parameters sequentially as they are provided in the csv.

The python api will require the parameters to be passed to run. 
It will require Database name,server/ip,username,password

Example:
========

python GenerateResApiOnDemand.py -in ~/testing.csv ~/restapi.py


Sample:
======

The example.csv file was used to generate example.py using this script.