import json
from flask import Flask, redirect, render_template, request, jsonify, make_response, abort, url_for

from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

from flask_sqlalchemy import SQLAlchemy

with open("secret.json") as f:
    SECRET = json.load(f)

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}".format(
    user=SECRET["user"],
    password=SECRET["password"],
    host=SECRET["host"],
    port=SECRET["port"],
    db=SECRET["db"])

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
db = SQLAlchemy(app)


class Hotel(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(30), unique=False)
    visitors = db.Column(db.Integer, unique=False)
    rooms = db.Column(db.Integer, unique=False)

    def __str__(self):
        return f"Name:{self.name} Number of visitors per year:{self.visitors}" \
               f" Number of rooms:{self.rooms}  "


class HotelSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Hotel
        sql_session = db.session

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    visitors = fields.Integer(required=True)
    rooms = fields.Integer(required=True)


hotel_schema = HotelSchema()
hotels_schema = HotelSchema(many=True)


@app.route("/home", methods=["GET"])
def get_all_hotels():
    all_hotels = Hotel.query.all()
    hotels = hotels_schema.dump(all_hotels)
    return render_template("index.html", hotels=hotels)


@app.route("/", methods=["GET", "POST"])
def create_hotel():
    if request.method == "POST":
        try:
            hotel = Hotel(
                name=request.form.get("name"),
                visitors=request.form.get("visitors"),
                rooms=request.form.get("rooms"))

            db.session.add(hotel)
            db.session.commit()
            return redirect(url_for('get_all_hotels'))
        except Exception as e:
            print("Failed to add hotel")
            print(e)

    return render_template("create.html")


@app.route("/update/<id>", methods=["POST", "GET", "PUT"])
def update_hotel(id):
    hotels = Hotel.query.get(id)
    if request.method == "POST":
        if hotels.name != request.form["name"]:
            hotels.name = request.form["name"]
        if hotels.visitors != request.form["visitors"]:
            hotels.visitors = request.form["visitors"]
        if hotels.rooms != request.form["rooms"]:
            hotels.rooms = request.form["rooms"]
        db.session.add(hotels)
        db.session.commit()
        return redirect(url_for('get_all_hotels'))

    return render_template("edit.html", hotels=hotels)


@app.route("/delete/<id>")
def delete_hotel(id):
    hotels = Hotel.query.get(id)
    db.session.delete(hotels)
    db.session.commit()
    return redirect(url_for('get_all_hotels'))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="127.0.0.1", port="3000")
