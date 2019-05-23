from flask import Blueprint
main = Blueprint('main', __name__)
 
import json
from engine import ClusteringEngine
 
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
from flask import Flask, request
 
@main.route("/cluster/<int:model>", methods=["GET"])
def get_cluster(model):
    print('get cluster')
    logger.debug("cluster centers requested")
    cluster_centers = clustering_engine.get_cluster(model)
    print (cluster_centers)
    return json.dumps(cluster_centers)

 
@main.route("/predict/<int:model>", methods = ["POST"])
def add_ratings(model):
    # get the predict from the Flask POST request object
    cons = int(request.form.get('annual_consumption'))
    cluster = clustering_engine.predict(model, cons)
 
    return json.dumps(cluster)
 
 
def create_app(spark_context, dataset_path):
    global clustering_engine

    clustering_engine = ClusteringEngine(spark_context, dataset_path)    
    
    app = Flask(__name__)
    app.register_blueprint(main)
    return app
