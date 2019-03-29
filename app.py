from flask import Flask, request, jsonify, json
from cassandra.cluster import Cluster
import requests
import sys

cluster = Cluster(['cassandra'])
session = cluster.connect()

app = Flask(__name__)

base_url = "http://makeup-api.herokuapp.com/api/v1/products.json?brand=maybelline"


@app.route('/')
def hello():
	name = request.args.get('name', 'World')
	return ('<h1>Hello, {}!<h1>'.format(name))

#get product from database
@app.route('/product/<int:id>', methods=['GET'])
def get_product_by_id(id):

	rows = session.execute("""SELECT * FROM makeup.products WHERE id=%(id)s""",{'id': id})
	data = None

	for row in rows:
		data = row
		print(row)

	#product_url = basee_url.format()

	resp = requests.get(base_url)

	if resp.ok:
		# print(resp.json())

		res = resp.json()

		matched = None
		for product in res:
			if product['id'] == id:
				matched = product
				break


		item = {
			'id': id,
			'name': data.name,
			'price': matched['price'],
			'description': matched['description']
		}


		return jsonify(item), resp.status_code
	else:
		return resp.reason


#insert product into database
@app.route('/items', methods= ['POST'])
def create_product():

	resp = requests.get(base_url)

	if resp.ok:
		# print(resp.json())

		res = resp.json()

		matched = None
		print('request',request.form['id'])

		for product in res:
			if product['id'] == int(request.form['id']):
				matched = product
				break
		print(request.form['id'])
		print(request.form['name'])
		print(matched)


	count_rows = session.execute("SELECT COUNT(*) FROM smartcart.products")

	for c in count_rows:
		last_id = c.count
	last_id += 1


	# print(request.args)
	resp = session.execute("INSERT INTO makeup.products(id,brand,description,name,price) VALUES(%s, %s, %s, %s, %s)", (int(request.form['id']),'maybelline', request.form['description'],request.form['name'], matched['price']))

	print('done')

	return jsonify({'message': 'added'}), 201

#delete product from database by itemid
@app.route('/deleteproduct/<int:id>', methods = ['DELETE'])
def delete_product_by_id(id):
	
	print('before delete')
	resp = session.execute("""DELETE FROM makeup.products WHERE id={}""".format(id))

	return jsonify({'message': 'deleted'.format(id)}), 200

#edit product into database
@app.route('/editproduct/<int:id>', methods = ['PUT'])
def update_product(id):

	print('inside put')

	

	print('inside update')
	rows = session.execute("""UPDATE makeup.products SET name=%(name)s, brand=%(brand)s ,description=%(description)s,price=%(price)s WHERE id=%(id)s""", {'name': request.form['name'], 'id': id, 'brand': 'maybelline', 'description':request.form['description'], 'price': request.form['price']})

	print('after update')

	return jsonify({'message':'1'.format(id)}), 200


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
