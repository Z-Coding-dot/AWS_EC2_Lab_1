from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

spark = SparkSession.builder.appName("Churn_No_Cat").getOrCreate()

data = spark.read.csv(
    "hdfs:/user/hadoop/churn_input/Churn_Modelling.csv",
    header=True,
    inferSchema=True
)

assembler = VectorAssembler(
    inputCols=[
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "EstimatedSalary"
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
    assembler,
    scaler,
    lr
])

model = pipeline.fit(data)
predictions = model.transform(data)

evaluator = MulticlassClassificationEvaluator(
    labelCol="Exited",
    predictionCol="prediction",
    metricName="accuracy"
)

accuracy = evaluator.evaluate(predictions)
print("Accuracy (No Categorical):", accuracy)

spark.stop()
