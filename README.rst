Home Data Centre
===========================

This project originates from my passion to automate the manual process which my father performs for his investment activities. He used to gather data from various online sources and paste them in an excel file for his analysis. I saw it as tedious and error-prone, so I looked for ways to automate it by teaching myself python.

It started out as a simple project where I scraped *ONE* data source online and put them straight into an excel for my father's consumption. However, the scope expanded and more data sources were required. Furthermore, raw data was no longer sufficient and data transformation was needed. Performing all these ETL steps in one single python programme became increasingly unmaintainable.

Since my first job as a python/data engineer in 2021, I learned the fundamentals of data engineering. I applied the knowledge acquired at work to my home setup and came up with the below architecture currently used at home. It has already gone through several cycles of revisions.

Initially, in 2021, I used several old lenovo laptops (2 with 4 GB RAM and 500GB HDD and 1 with 8GB ram with 1TB HDD) and create a cluster of computers connected via the home router. However, as data volume grows, I bought a Desktop with 64 GB RAM and placed it in the living room in March 2024. On the new desktop, I installed proxmox, a hypervisor capable of running Virtual Machines. As of March 2025, I am running several VMs on proxmox, each running a service accessible from a URL only resolvable using a DNS server with custom AAAA records in the home network.

This project not only provides tangible value for my father's investment activities, it also deepens my understanding of data engineering. I am planning to use the data to further explore the field of data science, machine learning and artificial intelligence.

Below is an overview of the architecture.


Architecture Overview
---------------------------


.. figure:: pics/Data_Platform_Architecture-Overview_Software_Architecture.drawio.svg
   :alt: Software Architecture

First and foremost, the investment activities the data is designed to support span across at least several days. In other words, real-timeness of the data is not necessary. This justifies the use of batch ingestion framework, like Apache Airflow.

I also expect data volume to increase over time, so I opted for Minio, the S3-compatible Object storage to store my data. Currently, I use Apache Iceberg as the file format to store the data. It is best supporte by Dremio, an open source Data Lakehouse whose value proposition is that it is only a compute engine and does not store data. In practice, Dremio connects to the data source directly (e.g. Minio) and fetches the data and return to the client, without storing a copy of the data.

For storing metadata of the ingestion (e.g. Airflow's DAGs, ingestion logs of a custom ingestion framework I wrote etc. etc.), I use postgres. Row-by-row insertion is best with RDBMS like postgres, while bulk insertion is best with big data file format, like Apache Iceberg. I discovered this after experiencing the pain of ever-increasing file size of iceberg with row-by-row insertion.










.. figure:: pics/Data_Platform_Architecture-ETL_Data_Distribution_Apps.drawio.svg
   :alt: Minio Main Page

   Minio



