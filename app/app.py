from flask import Flask, session, render_template, request
from Translate import SMTReq, SMTDes

class MyServer(Flask):

    def __init__(self, *args, **kwargs):
            super(MyServer, self).__init__(*args, **kwargs)
            self.sid = 0
            self.data_obj = {}
            self.design_obj = {}

app = MyServer(__name__)

@app.route('/')
def index() :
	session['sid'] = app.sid
	app.sid += 1
	print('New session with id : ', session['sid'])
	return render_template('index.html')

@app.route('/design/', methods=['POST'])
def design() :
	lang1 = request.form['lang1']
	lang2 = request.form['lang2']
	lm_in = request.form['lm_in']
	pt_out = request.form['pt_out']
	lm_out = request.form['lm_out']
	app.design_obj[session['sid']] = SMTDes(lang1, lang2, lm_in, pt_out, lm_out)
	app.data_obj[session['sid']] = SMTReq(pt_out, lm_out)
	return render_template('translate.html', result='') 


@app.route('/data/', methods=['POST'])
def data() :
	pt = request.form['pt']
	lm = request.form['lm']
	app.data_obj[session['sid']] = SMTReq(pt, lm)
	return render_template('translate.html', result='')

@app.route('/translate/', methods=['POST'])
def translate() :
	sentence = request.form['sent']
	if session['sid'] in app.data_obj and app.data_obj[session['sid']] is not None :
		t = app.data_obj[session['sid']].translate(sentence)
		return render_template('translate.html', result=t)
	else :
		return render_template('error.html' , error='No translation system selected')

if __name__ == '__main__':
	app.secret_key = 'A0Zr98j/3yXR~XHH!jmN]LWX/,?RT'
	app.run(debug=True)