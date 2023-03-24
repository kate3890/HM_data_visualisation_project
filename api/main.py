
from flask import Flask, request, jsonify
from flask_restx import Resource, Api
from pymysql import connect
from pymysql.cursors import DictCursor

app = Flask(__name__)
api = Api(app)

# Database connection parameters

db_config = {
    "host": "34.175.52.97",
    "user": "root",
    "password": "G_4xbGLV4D{0aMD0",
    "database": "main",
}

# Connecting to the data in MySQL

def get_db_connection():
    return connect(**db_config)

def fetch_data_from_db(query):
    connection = get_db_connection()
    cursor = connection.cursor(DictCursor)
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    connection.close()
    return {"data": data, "columns": columns}

# Creating EndPoints fr each data set

class Articles(Resource):
    def get(self):
        return jsonify(fetch_data_from_db("SELECT * FROM articles LIMIT 1000"))

class Transactions(Resource):
    def get(self):
        return jsonify(fetch_data_from_db("SELECT * FROM transactions LIMIT 1000"))

class Customers(Resource):
    def get(self):
        return jsonify(fetch_data_from_db("SELECT * FROM customers LIMIT 1000"))

# Filtering customer data endpoint (used for filters)

class FilteredCustomers(Resource):
    def get(self):
        min_age = request.args.get("min_age", 0, type=int)
        max_age = request.args.get("max_age", 100, type=int)
        club_member_status = request.args.get("club_member_status", "ACTIVE")
        fashion_news_frequency = request.args.get("fashion_news_frequency", "Regularly")

        query = f"""
            SELECT customer_id, age, club_member_status, fashion_news_frequency
            FROM customers
            WHERE age BETWEEN {min_age} AND {max_age}
            AND club_member_status = '{club_member_status}'
            AND fashion_news_frequency = '{fashion_news_frequency}'
            LIMIT 1000;
        """
        return jsonify(fetch_data_from_db(query))

# Filtered articles data endpoint (used for filters)

class FilteredArticles(Resource):
    def get(self):
        perceived_colours = request.args.get("perceived_colours", "")
        garment_group_name = request.args.get("garment_group_name", "")

        # Split the comma-separated string and wrap each color in quotes
        perceived_colours_list = [f"{color.strip()}" for color in perceived_colours.split(",") if color.strip()]

        # Join the list back into a string with commas and single quotes
        perceived_colours_formatted = ",".join(f"'{color}'" for color in perceived_colours_list)

        query = f"""
        SELECT *
        FROM articles
        WHERE perceived_colour_master_name IN ({perceived_colours_formatted})
        AND garment_group_name = '{garment_group_name}'
        LIMIT 1000;
        """
        return jsonify(fetch_data_from_db(query))


# Linking the datasets to be used later in the stramlit app

api.add_resource(FilteredArticles, "/api/filtered_articles")
api.add_resource(FilteredCustomers, "/api/filtered_customers")
api.add_resource(Articles, "/api/articles")
api.add_resource(Transactions, "/api/transactions")
api.add_resource(Customers, "/api/customers")

if __name__ == "__main__":
    app.run(debug=True)
