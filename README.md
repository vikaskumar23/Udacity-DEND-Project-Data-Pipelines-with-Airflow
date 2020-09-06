## Udacity Data Engineering Project: Data Pipelines with Airflow
The objective of this project is to orchestrate the data pipeline using Airflow. Airflow manages all the steps in data pipeline automatically with schedules. This will allow the analytics team and business to introduce more automation and monitoring to their data warehouse ETL pipelines

## Introduction
In this project ETL Pipeline is automated using an orchestration tool called ```Airflow```. It performs all the steps in a coordinated manner and it allows parallelism in tasks whenever possible.
The source data resides in S3 and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.

## Airflow Overview

Airflow is a ```Workflow engine``` which means:

- Manage scheduling and running jobs and data pipelines
- Ensures jobs are ordered correctly based on dependencies
- Manage the allocation of scarce resources
- Provides mechanisms for tracking the state of jobs and recovering from failure

It is highly versatile and can be used across many many domains. To read more about **Airflow** [click here](https://airflow.apache.org/docs/stable/)

# Project Scope
This project is developed to automate and monitor all the data pipeline tasks.

It provides many benifts to data engineers, analysts like
- No manual intervention is required.
- All steps taken care, Pipeline automatically stops if any dependent task is blocked.
- No chance of error.
- It has realtime alerting feature too, that helps in monitoring if anything goes bad.
- Business operations run smooth.
And many more...

## Data Required for Project
#### Song Dataset
The first dataset is a subset of real data from the [Million Song](https://labrosa.ee.columbia.edu/millionsong/) Dataset. Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID. For example, here are filepaths to two files in this dataset:
```
song_data/A/B/C/TRABCEI128F424C983.json
song_data/A/A/B/TRAABJL12903CDCF1A.json
```
And below is an example of what a single song file, TRAABJL12903CDCF1A.json, looks like:
```
{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}
```

## Data Model
Using the song and log datasets, data is transformed into Star Schema, so that it can be queries easily and understandable to analysts and business users.
First Data is fetched from S3 bucket to staging tables.
![Staging Tables](https://github.com/vikaskumar23/Udacity-DEND-Project-Data-Warehouse-on-Redshift/blob/master/staging_tables.PNG)

Then after some transformations data is loaded into star Schema. Some transformations include:
- Date data is divided in chunks to create date dimension.
- Songs data and events data is joined to create songplays fact data.
- Duplicate data is removed before transforming to star schema.

The resulting star schema consists of one fact table and four dimension tables.
![Data Model](https://github.com/vikaskumar23/Udacity-DEND-Project-Data-Warehouse-on-Redshift/blob/master/dbmodel.png)
##### Fact Table
- **songplays:** records in log data associated with song plays i.e. records with page ```NextSong```
    - **songplay_id:** unique id for each songplay event
    - **start_time:** start time of event (timestamp)
    - **user_id:** user_id of user
    - **level:** it shows user is paid subscriber or not
    - **song_id:** id of the played song
    - **artist_id:** id of artist
    - **session_id:** id of the current session
    - **location:** location of artist
    - **user_agent:** device/software to access sparkify app

##### Dimension Tables
- **users:** users in the app
    - **user_id:** unique id of user
    - **first_name:** first name of user
    - **last_name:** last name of user
    - **gender:** gender of user
    - **level:** it shows user is paid subscriber or not
- **songs:** songs in music database
    - **song_id:** unique id of song
    - **title:** name of the song
    - **artist_id:** id of artist
    - **year** year in which song is created
    - **duration:** duration of song in seconds
- **artists:** artists in music database
    - **artist_id:** unique id of artist
    - **name:** name of the artist
    - **location:** location of the artist
    - **latitude** latitude of artist location
    - **longitude:** longitude of artist location
- **time:** timestamps of records in songplays broken down into specific units
    - **start_time:** start time timestamp
    - **hour:** hour of event
    - **day:** day of event
    - **week** week of event
    - **month:** month of event
    - **year:** year of event
    - **weekday:** weekday of event

## ETL Pipeline DAG
![Dag]()

![Dag Run]()

The pipeline is divided in mainly 5 tasks:
1. All the required staging, fact and dimension tables are created.
2. Event and Song Data is loaded in staging tables.
3. songplays fact table is loaded by joining song and event staged data.
4. All the dimension tables are loaded.
5. Data Quality checks are completed.

## Data Pipeline Configuration
- **Schedule:** hourly
- **catchup:** False (Do not backfill)
- **depends_on_past:** False (Two scheduled dags can run simultaneously)

## Custom Operators used in this project
Airflow allows to create custom operators and hooks to extend the features and usability of Airflow.

For this project we created four custom operators, details are given below.

1. **StageToRedshiftOperator:** load data from s3 bucket to staging tables in Redshift.
2. **LoadFactOperator:** load fact table by joining events and songs staging table.
3. **LoadDimensionOperator:** load dimension tables using events and songs staging table.
4. **DataQualityOperator:** Perform quality checks on newly created tables.

## Project Directory and Files
- **airflow/dags:** 
	- **udac_example_dag.py:** dag file containing all the tasks to perform and its sequence to run.
	- **create_tables_sql:** Sql file containing all the statements to create tables in Amazon Redshift.
- **airflow/plugins/operators**
	- **\__init__.py:** To treat directory as modules
	- **load_fact.py:** LoadFactOperator Custom Operator Declaration
	- **load_dimension.py:** LoadDimensionOperator Custom Operator Declaration
	- **stage_redshift.py:** StageToRedshiftOperator Custom Operator Declaration
	- **data_quality.py:** DataQualityOperator Custom Operator Declaration
- **airflow/plugins/helpers**
	- **sql_queries.py:** Sql file containing all the sql queries that are needed in ETL Pipeline

## Project Execution
#### Steps
1. Setup Airflow, and start scheduler and webserver
2. Move the dags and plugins in the airflow dag directory when scheduler look for dags, many time it will be ```/home/airflow/airflow/``` directory
3. In Airflow webpage Connections create connection with AWS and Redshift
    - **AWS:** Fill connection name as aws_credentials, connection type as 'Amazon Web Services' login and password with aws_access_key and aws_secret_access_key respectively.
    - **Redshift:** Fill Connection name as redshift, connection type as Postgres, schema as database name, user as db username, password as dbpassword, host as redshift cluster access URL and port as 5439.
 4. Trigger the dag from dags page.

## References
www.udacity.com

https://airflow.apache.org/docs/stable/

https://github.com/apache/airflow

https://www.astronomer.io/guides/