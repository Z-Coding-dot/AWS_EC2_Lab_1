# Spark ML Pipeline on Amazon EMR

Customer churn prediction using Apache Spark ML Pipeline on Amazon EMR.

## Dataset
- Bank Customer Churn Dataset (Kaggle)
- Target column: Exited

## Files
- churn_pipeline.py — Full Spark ML pipeline with categorical features
- churn_pipeline_nocat.py — Feature ablation version (no categorical features)

## HDFS Path
/user/hadoop/churn_input/Churn_Modelling.csv

## Run Commands
```bash
spark-submit --master yarn --deploy-mode client churn_pipeline.py
spark-submit --master yarn --deploy-mode client churn_pipeline_nocat.py


Evaluation

Metric: Accuracy

Comparison between full pipeline and ablated pipeline

Platform

Amazon EMR

Apache Spark

Hadoop (HDFS)`