from flask import Flask
from flask import render_template, redirect, url_for, request, abort, flash, session

app = Flask(__name__)

import json
import time
import pycurl
from io import BytesIO

def wallet_com(data):
	x = 0
	while x < 8:
		try:
			buffer = BytesIO()
			c = pycurl.Curl()
			c.setopt(c.URL, '127.0.0.1')
			c.setopt(c.PORT, 7076)
			c.setopt(c.POSTFIELDS, json.dumps(data))
			c.setopt(c.WRITEFUNCTION, buffer.write)

			output = c.perform()

			c.close()

			body = buffer.getvalue()
			#print(body)
			parsed_json = json.loads(body.decode('iso-8859-1'))
			return parsed_json
			break
		except:
			print('error with wallet')
			x = x + 1


@app.route('/')
def start():
    return render_template('start.html')

@app.route("/redirect", methods=["POST"])
def address_redirect():
        address_block=request.form['xrb_address_block']
        complete_address = '/search/' + address_block
        return redirect(complete_address)

@app.route('/search/<address>')
def search(address=None):

	if len(address) is 64 and address[:4] == 'xrb_':
		xrb_address = address
		frontier_data = { "action": "frontiers", "account": xrb_address, "count": "1" }
		parsed_json = wallet_com(frontier_data)
		if xrb_address in parsed_json['frontiers']:
			frontier_block = parsed_json['frontiers'][xrb_address]
			history_data = { "action": "history", "hash": frontier_block, "count": 100 }
			parsed_json = wallet_com(history_data)

			items = []
			for i in parsed_json['history']:
				f_amount = float(i['amount']) / 1000000000000000000000000.0
				xrb_amount = format((float(f_amount) / 1000000.0), '.6f')
				item_data = dict(account=i['account'], amount=xrb_amount, type=i['type'], hash=i['hash'])
				items.append(item_data)

		else:
			items = []
			item_data = dict(account='No Hx', amount='No Hx', type='No Hx', hash='No Hx')
			items.append(item_data)

		return render_template('address.html', address=address, items=items)

	elif len(address) is 64:
		block = address
		return render_template('block.html', block=block)
	else:
		return render_template('error.html', error=address)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
