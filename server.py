import time, sys, cherrypy, os
from paste.translogger import TransLogger
from app import create_app
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession

def init_spark_context():
    # load spark context
    spark = SparkSession.builder.appName("python clustering").getOrCreate()

    # IMPORTANT: pass aditional Python modules to each worker
    engine = os.path.join(os.getcwd(), "engine.py")
    app = os.path.join(os.getcwd(), "app.py")
    spark.sparkContext.addPyFile(engine)
    spark.sparkContext.addPyFile(app)

    return spark
 
def run_server(app):
 
    # Enable WSGI access logging via Paste
    app_logged = TransLogger(app)
 
    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, '/')
 
    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload.on': True,
        'log.screen': True,
        'server.socket_port': 9999,
        'server.socket_host': '0.0.0.0'
    })
 
    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()
 
 
if __name__ == "__main__":
    # Init spark context and load libraries
    spark = init_spark_context()
    dataset_path = os.path.join('consumer')
    app = create_app(spark, dataset_path)
 
    # start web server
    run_server(app)