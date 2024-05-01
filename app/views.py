import json
import os
import requests
from flask import render_template, redirect, request,send_file
from werkzeug.utils import secure_filename
from app import app
from timeit import default_timer as timer


request_tx = []

files = {}

UPLOAD_FOLDER = "app/static/Uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ADDR = "http://127.0.0.1:8800"



def get_tx_req():
    global request_tx
    chain_addr = "{0}/chain".format(ADDR)
    resp = requests.get(chain_addr)
    if resp.status_code == 200:
        content = []
        chain = json.loads(resp.content.decode())
        for block in chain["chain"]:
            for trans in block["transactions"]:
                trans["index"] = block["index"]
                trans["hash"] = block["prev_hash"]
                content.append(trans)
        request_tx = sorted(content,key=lambda k: k["hash"],reverse=True)



@app.route("/")
def index():
    get_tx_req()
    return render_template("index.html",title="FileStorage",subtitle = "A Decentralized Network for File Storage/Sharing",node_address = ADDR,request_tx = request_tx)


@app.route("/submit", methods=["POST"])

def submit():
    start = timer()
    user = request.form["user"]
    up_file = request.files["v_file"]
    
    
    up_file.save(os.path.join("app/static/Uploads/",secure_filename(up_file.filename)))
    
    files[up_file.filename] = os.path.join(app.root_path, "static" , "Uploads", up_file.filename)
    
    file_states = os.stat(files[up_file.filename]).st_size 
    
    post_object = {
        "user": user, 
        "v_file" : up_file.filename, 
        "file_data" : str(up_file.stream.read()), 
        "file_size" : file_states   
    }
   
    
    address = "{0}/new_transaction".format(ADDR)
    requests.post(address, json=post_object)
    end = timer()
    print(end - start)
    return redirect("/")


@app.route("/submit/<string:variable>",methods = ["GET"])
def download_file(variable):
    p = files[variable]
    return send_file(p,as_attachment=True)
