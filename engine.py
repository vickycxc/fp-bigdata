import os
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
import pandas

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClusteringEngine:
    """Clustering engine
    """

    def __process_dataset(self):
        """Making model from dataset
        """
        data = []
        for i in range (len(self.model)):
            logger.info("Training consumers batch {}".format(i))

            logger.info("Assembling vector!")
            assembler = VectorAssembler(
            inputCols=["_c12"],
            outputCol='features')

            data.append(assembler.transform(self.model[i]))

            logger.info("Training Model!")
            kmeans = KMeans().setK(10).setSeed(1)
            self.model[i] = kmeans.fit(data[i])

            logger.info("Making Preditction!")
            self.predictions = self.model[i].transform(data[i])
    
            logger.info("Clustering model built!")

    def predict(self, model, cons):
        """Get Prediction
        """
        #data = self.spark.createDataFrame([(user_id, anime_id, ratings)],["user_id", "anime_id", "rating"])
        # input = self.spark.createDataFrame([("1","2","3","4","5","6","7","8","9","10","11",cons,"13","14")],["net_manager","purchase_area","street","zipcode_from","zipcode_to","city","delivery_perc","num_connections","perc_of_active_connections","type_conn_perc","type_of_connection","annual_consume","annual_consume_lowtarif_perc","smartmeter_perc"])
        center = self.model[model].clusterCenters()

        temp = []
        for elements in center:
            dist = abs(elements-cons)
            temp.append(dist)
        
        cluster = temp.index(min(temp))+1

        logger.info(cluster)
        
        return cluster

    def get_cluster(self,model):
        """Get cluster centers
        """
        list = []
        centers = self.model[model].clusterCenters()
        print (centers)
        print("Cluster Centers: ")
        for center in centers:
            list.append(center.tolist())

        return list

    def __init__(self, spark, dataset_path):

        logger.info("Starting up the Clustering Engine: ")

        self.spark = spark

        self.model = []

        # Load ratings data for later use
        logger.info("Loading consumers data...")

        for filename in sorted(os.listdir(dataset_path)):
            if filename.endswith(".csv"):
                batch = os.path.join(dataset_path, filename)
                logger.info("Loading {}".format(filename))
                self.model.append( spark.read.csv(batch, header=False, inferSchema=True))
                continue
            else:
                continue

        logger.info("done loading!")

        # logger.info("Loading consumers data...")
        # batch0 = os.path.join(dataset_path, 'output0.csv')
        # batch1 = os.path.join(dataset_path, 'output1.csv')
        # batch2 = os.path.join(dataset_path, 'output2.csv')
        # logger.info("Loading consumers batch 0")
        # self.model.append( spark.read.csv(batch0, header=True, inferSchema=True))
        # logger.info("Loading consumers batch 1")        
        # self.model.append( spark.read.csv(batch1, header=True, inferSchema=True))
        # logger.info("Loading consumers batch 2")        
        # self.model.append( spark.read.csv(batch2, header=True, inferSchema=True))

        self.__process_dataset() 
