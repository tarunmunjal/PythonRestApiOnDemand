# PythonRestApiOnDemand
This project is to provide a functional restapi.


Below are the requirments:

Backend should be MySQL.

Any calls to backend are made using Stored Procedures.
Stored procedure must be able to handle null values passed to them for optional parameters.
If the route contains variable e.g. /this/test/<string:param1>/<string:param2> param1 and param2 will be the first two params
in your stored procedure call.
Stored procedre call will contain all the parameters sequentially as they are provided in the csv.

I can provide a Dokerfile and all the necessary file to run the resultant RestApi in Docker image.

The python api will require the parameters to be passed to run. 
It will require Database name,server/ip,username,password

Create a PR with the csv file for the RESTApi you need and I will generate the api and email it to you.
