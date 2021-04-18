from flask import Flask, request, jsonify, send_file, url_for
from flask_restful import Api, Resource
from pymongo import MongoClient
# from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")
db = client["Db1"]
User = db["User"] #add new collection called User to the database Db1

class Register(Resource):
    def post(self):
        user_data = request.get_json()
        username = user_data["username"]
        password = user_data["password"]
    
        if len(username) < 4:
            jsontext = {
                "Message" : "Username must be at least 4 characters",
                "Status" : 302
            }
            return jsonify(jsontext)
        elif len(password) < 4:
            jsontext = {
                "Message" : "Password must be at least 4 characters",
                "Status" : 302
            }
            return jsonify(jsontext)
        elif User.count_documents({"username" : username}) != 0:
            jsontext = {
                "Message" : "Account already created",
                "Status" : 302
            }
            return jsonify(jsontext)
        else:
            
            User.insert_one({
                "username" : username,
                "password" : password,
                "token" : 10,
                "sentences" : []
            })
            
            jsontext = {
                "Message" : "Account created successfully!",
                "Status" : 200
            }

            return jsonify(jsontext)
                
class StoreSentence(Resource):
    def post(self):
        user_data = request.get_json()
        username = user_data["username"]
        password = user_data["password"]
        new_sentence = user_data["sentences"]

        if User.count_documents({"username" : username}) == 0:
            jsontext = {
                "Message" : "Username not found",
                "Status" : 302
            }
            return jsonify(jsontext)
        elif password != User.find({"username":username})[0]["password"]:
            jsontext = {
                "Message" : "Password is not correct",
                "Status" : 302
            }
            return jsonify(jsontext)
        elif User.find({"username" : username})[0]["token"] == 0:
            #make sure users'tokens always greater or equal to 0
            User.update_one({"username":username}, {"$set": {"token": 0} })
            jsontext = {
                "Message" : "Not enough token. Please refill",
                "Status" : 301
            }
            return jsonify(jsontext)
        elif len(new_sentence) == 0:
            jsontext = {
                "Message" : "Please enter a sentence",
                "Status" : 301
            }
            return jsonify(jsontext)
        else: 
            #after checking for usr, pw and token successfully, substract 1 token and insert users' sentences
            new_token = User.find({"username": username})[0]["token"] - 1
            User.update_one(
                {"username":username}, 
                {"$set" : {"token":new_token} }
            )
            User.update_one(
                {"username":username},
                {"$push": {"sentences": new_sentence} } 
            )
            jsontext = {
                "Message" : "Added sentence successfully",
                "Status" : 200
            }
            return jsonify(jsontext)

class RetrieveSentence(Resource):
    def get(self):
        user_data = request.get_json()
        username = user_data["username"]
        password = user_data["password"]

        if User.count_documents({"username" : username}) == 0:
            jsontext = {
                "Message" : "Username not found",
                "Status" : 302
            }
            return jsonify(jsontext)
        elif password != User.find({"username":username})[0]["password"]:
            jsontext = {
                "Message" : "Password is not correct",
                "Status" : 302
            }
            return jsonify(jsontext)
        else: 
            #retrieve the token and the whole list of sentences of user
            user = User.find({"username":username})[0]
            returned_token = user["token"]
            returned_sentences = user["sentences"]
            jsontext = {
                "Message" : "Retrieved successfully",
                "Status" : 200,
                "username" : username,
                "token" : returned_token,
                "sentences" : returned_sentences
            }
            return jsonify(jsontext)




api.add_resource(Register,"/register")
api.add_resource(StoreSentence,"/store_sentence")
api.add_resource(RetrieveSentence,"/retrieve_sentence")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")



        












"""
app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017") #27017 is the default port for pymongo, client can contain many independent databases
db = client["NewDB"] #add a new database
UserNum = db["UserNum"] #add a new collection inside the database
"""



