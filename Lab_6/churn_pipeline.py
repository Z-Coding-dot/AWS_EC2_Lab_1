from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    StringIndexer,
    OneHotEncoder,
    VectorAssembler,
    StandardScaler
)
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

spark = SparkSession.builder.appName("CustomerChurnPipeline").getOrCreate()

data = spark.read.csv(
    "hdfs:/user/hadoop/churn_input/Churn_Modelling.csv",
    header=True,
    inferSchema=True
)

geo_indexer = StringIndexer(
    inputCol="Geography",
    outputCol="GeographyIndex"
)

gender_indexer = StringIndexer(
    inputCol="Gender",
    outputCol="GenderIndex"
)

encoder = OneHotEncoder(
    inputCols=["GeographyIndex", "GenderIndex"],
    outputCols=["GeographyVec", "GenderVec"]
)

assembler = VectorAssembler(
    inputCols=[
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "EstimatedSalary",
        "GeographyVec",
        "GenderVec"
    ],
    outputCol="features"
)

scaler = StandardScaler(
    inputCol="features",
    outputCol="scaledFeatures"
)

lr = LogisticRegression(
    labelCol="Exited",
    featuresCol="scaledFeatures"
)

pipeline = Pipeline(stages=[
    geo_indexer,
    gender_indexer,
    encoder,
    assembler,
    scaler,
    lr
])

model = pipeline.fit(data)

predictions = model.transform(data)

predictions.select(
    "Exited",
    "prediction",
    "probability"
).show(10)

evaluator = MulticlassClassificationEvaluator(
    labelCol="Exited",
    predictionCol="prediction",
    metricName="accuracy"
)

accuracy = evaluator.evaluate(predictions)
print("Accuracy:", accuracy)

spark.stop()
