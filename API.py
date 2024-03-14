from flask import Flask, Response, request
import logging
import os
import json
import subprocess

app = Flask(__name__)

def check_database_connection():
    try:
        connection = psycopg2.connect(user="Username",
                                      password="Password",
                                      host="host number",
                                      port="port number",
                                      database="Database")
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        connection.close()
        return True
    except OperationalError as e:
        print(f"Database connection failed: {e}")
        return False


def check_kubernetes_connection():
    try:
        result = subprocess.run(["kubectl", "get", "nodes"], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print("Kubernetes cluster connection successful")
            return True
        else:
            print("Kubernetes cluster connection failed")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Kubernetes command failed: {e}")
        return False

def check_docker_connection():
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print("Docker connection successful")
            return True
        else:
            print("Docker connection failed")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Docker command failed: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    try:
        is_healthy = check_database_connection() and check_kubernetes_connection() and check_docker_connection()

        if is_healthy:
            health_info = {
                "status": "up",
                "api_version": "1.0",
                "environment": os.getenv("FLASK_ENV", "production")
            }
            return Response(json.dumps(health_info), mimetype='application/json'), 200
        else:
            logging.error("Health check failed")
            return Response(json.dumps({"status": "down", "error": "Health check failed"}), mimetype='application/json'), 503
    except Exception as e:
        logging.error(f"Health check exception: {e}")
        return Response(json.dumps({"status": "down", "error": str(e)}), mimetype='application/json'), 503

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    port = os.getenv('PORT', 8080)
    app.run(host='0.0.0.0', port=port)
