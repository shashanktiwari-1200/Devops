import os
import logging
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

# -----------------------------------------
#  Logging Configuration
# -----------------------------------------
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

logger = logging.getLogger(__name__)

app = Flask(__name__)


# -----------------------------------------
#  Database Connection
# -----------------------------------------
# def get_db_connection():
#     try:
            
#             conn = mysql.connector.connect(
#               host=os.getenv("DB_HOST"),
#               user=os.getenv("DB_USER"),
#               password=os.getenv("DB_PASSWORD"),
#               database=os.getenv("DB_NAME")
#         )
#         logger.info("Database connection established successfully")
#         return conn
#     except Exception as e:
#         logger.error(f"Database connection failed: {str(e)}")
#         raise

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        logger.info("Database connection established successfully")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise


# -----------------------------------------
#  GET API — Fetch all data
# -----------------------------------------
@app.route('/get-data', methods=['GET'])
def get_data():
    logger.info("GET /get-data called")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM cricketer")
        rows = cursor.fetchall()

        logger.info(f"GET /get-data success — returned {len(rows)} records")
        return jsonify(rows), 200

    except Exception as e:
        logger.error(f"Error in GET /get-data: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        try:
            cursor.close()
            conn.close()
            logger.info("Database connection closed (GET)")
        except:
            pass


# -----------------------------------------
#  POST API — Insert data
# -----------------------------------------
@app.route("/add-data", methods=["POST"])
def add_data():
    req_data = request.get_json()
    logger.info(f"POST /add-data — incoming payload: {req_data}")

    if not req_data:
        logger.warning("POST /add-data — missing JSON body")
        return jsonify({"error": "Missing JSON payload"}), 400

    try:
        CricketerID = req_data.get('CricketerID')
        CricketerName = req_data.get('CricketerName')
        TypeCricket = req_data.get('TypeCricket')

        if not CricketerID or not CricketerName or not TypeCricket:
            logger.warning("POST /add-data — missing required fields")
            return jsonify({"error": "Missing CricketerID, CricketerName or TypeCricket"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "INSERT INTO cricketer (CricketerID, CricketerName, TypeCricket) VALUES (%s, %s, %s)"
        cursor.execute(query, (CricketerID, CricketerName, TypeCricket))
        conn.commit()

        logger.info(f"POST /add-data success — inserted ID: {CricketerID}")

        return jsonify({
            "message": "Record inserted successfully",
            "inserted_id": CricketerID
        }), 201

    except Exception as e:
        logger.error(f"Error in POST /add-data: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        try:
            cursor.close()
            conn.close()
            logger.info("Database connection closed (POST)")
        except:
            pass


# -----------------------------------------
#  DELETE API — Delete by CricketerID
# -----------------------------------------
@app.route("/delete-data/<int:CricketerID>", methods=["DELETE"])
def delete_data(CricketerID):
    logger.info(f"DELETE /delete-data/{CricketerID} called")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "DELETE FROM cricketer WHERE CricketerID = %s"
        cursor.execute(query, (CricketerID,))
        conn.commit()

        if cursor.rowcount == 0:
            logger.warning(f"DELETE failed — ID {CricketerID} not found")
            return jsonify({"message": "No record found with the given CricketerID"}), 404

        logger.info(f"DELETE success — ID {CricketerID} removed")
        return jsonify({"message": "Record deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error in DELETE /delete-data/{CricketerID}: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        try:
            cursor.close()
            conn.close()
            logger.info("Database connection closed (DELETE)")
        except:
            pass


# -----------------------------------------
# Run Flask App
# -----------------------------------------
if __name__ == '__main__':
    logger.info("Flask app started on http://localhost:5000")
    #   app.run(debug=True)
    app.run(host="0.0.0.0", port=5000,debug=True)
