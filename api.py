from flask import Flask, request
from flask_restful import Resource, Api
import csv
import datetime

app = Flask(__name__)
api = Api(app)

# Classes
class TransactionCreate(Resource):
	#Create transaction
	def post(self):
		error = {
			"toAccount": True,
			"fromAccount": True,
			"balance": False
		}

		#Movement
		with open('accounts.csv', 'r') as readFile:
			reader = csv.reader(readFile)
			lines = list(reader)

		for row in lines:
			#Add amount
			if(row[0] == request.form['toAccount']):
				row[1] = round(float(row[1]) + float(request.form['amount']))
				error['toAccount'] = False
			#Decrease amount
			if(row[0] == request.form['fromAccount']):
				row[1] = round(float(row[1]) - float(request.form['amount']))
				error['fromAccount'] = False
				if(row[1] < -500):
					error['balance'] = True

		#Check errors
		if(error['toAccount']):
			return {"Error": "Destiny account not found"}, 404

		if(error['fromAccount']):
			return {"Error": "Origin account not found"}, 404

		if(error['balance']):
			return {"Error": "Balance insuficient"}, 400

		#If OK inssert and update
		with open('accounts.csv', 'w', newline='') as writeFile:
			writer = csv.writer(writeFile)
			writer.writerows(lines)
		readFile.close()
		writeFile.close()

		#Insert transaction
		now = datetime.datetime.now()
		row = [request.form['fromAccount'], request.form['toAccount'], request.form['amount'], now.strftime("%Y-%m-%dT%H:%M:%S.%f")]
		with open('transactions.csv', 'a', newline='') as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(row)
		csvFile.close()

class TransactionRead(Resource):
	#Get transaction
	def get(self, account, transactions):
		notFound = True
		response = {
			"transactions": []
		}

		with open('transactions.csv', 'r') as readFile:
			reader = csv.reader(readFile)
			lines = list(reader)

		for row in lines:
			#Select row
			if(row[0] == account and (transactions == "sent" or transactions == "all") ):
				item = {
					"fromAccount": row[0],
					"toAccount": row[1],
					"amount": row[2],
					"sentAt": row[3]
				}
				response['transactions'].append(item)

			if(row[1] == account and (transactions == "received" or transactions == "all") ):
				item = {
					"fromAccount": row[0],
					"toAccount": row[1],
					"amount": row[2],
					"sentAt": row[3]
				}
				response['transactions'].append(item)

		readFile.close()

		if(len(response['transactions']) == 0):
			return "No transactions foud", 404

		return response

class Account(Resource):
	#Get transaction
	def get(self, account):
		response = {
			"balance": []
		}

		with open('accounts.csv', 'r') as readFile:
			reader = csv.reader(readFile)
			lines = list(reader)

		for row in lines:
			#Select row
			if(row[0] == account):
				item = {
					"account": row[0],
					"balance": row[1],
					"owner": row[2],
					"createdAt": row[3]
				}
				response['balance'].append(item)

		readFile.close()

		if(len(response['balance']) == 0):
			return "Account not foud", 404

		return response
		
# URL's
api.add_resource(TransactionCreate, '/api/transaction')
api.add_resource(TransactionRead, '/api/transaction/<account>/<transactions>')
api.add_resource(Account, '/api/account/<account>')

if __name__ == '__main__':
 app.run(debug=True)