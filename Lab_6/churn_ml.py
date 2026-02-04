from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline

spark = SparkSession.builder.appName("ChurnML").getOrCreate()

data = spark.read.csv(
    "hdfs:/user/hadoop/churn_input/Churn_Modelling.csv",
    header=True,
    inferSchema=True
)

indexer = StringIndexer(
    inputCol="Gender",
    outputCol="GenderIndex"
)

assembler = VectorAssembler(
    inputCols=[
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
        "GenderIndex"
    ],
    outputCol="features"
)

lr = LogisticRegression(
    featuresCol="features",
    labelCol="Exited"
)

pipeline = Pipeline(stages=[indexer, assembler, lr])

model = pipeline.fit(data)

predictions = model.transform(data)
predictions.select("Exited", "prediction").show(10)

spark.stop()
