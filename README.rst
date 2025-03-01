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

The data consumers are Apache Superset and a bespoke data client GUI I made with PySide. Apache Superset is a general purpose Business Intelligence tool. With that, I can visualise price movements with line chart, create data quality dashboards on data freshness and row counts inspection, send out reports at regular intervals to gmail accounts and so on. While powerful, it is not a complete replacement for all data applications. For instance, my father has a specific requirement on the format of an Excel file which he uses for his investment activities. Therefore, I created a GUI with PySide which exposes parameters like dates and stock code for my father to key in, connects to and extracts data from Dremio and dumps the result in Excel. 

.. figure:: pics/Data_Platform_Architecture-Overview_Platform_Infrastructure.drawio.svg
   :alt: Platform Architecture

To support all the applications above, an easily maintainable platform is required. For that, I use proxmox, a hypervisor which can run Virtual Machines and LXD containers (this of them as light weight VMs). It is built on the Linux Debian distro and comes with a GUI accessible remotely. One can easily create Virtual Machines, assign CPU and RAM to it and install any operation system which come in an .iso file downloaded online.

When deciding how to group the applications when deploying them on the proxmox Virtual Machines, I opt for separating stateful and stateless applications.

- Stateful applications like Postgres and Minio should all run in its own virtual machines. It allows easy rollback and data backup.
- Stateless applications all run on kubernetes, which in turn run in one virtual machine. This allows easy deployment via helm chart, which abounds online.
- Infrastructure-critical applications (e.g. DNS and DHCP server, docker container registry/package artifactory) should also run in separate LXD containers. This ensures that basic functionalities are guaranteed even when kubernetes fails (e.g. resource contention of applications in kubernetes)

For Networking, I use Technitium. It has many features, but I only use it as a DHCP server (which assigns IP addresses to the Virtual Machines and LXD containers) and DNS server (which resolves human readable URLs to IP addresses). With that, for instance, I can easily access my Minio buckets via a URL like `http://minio-prod` instead of `http://192.168.1.10`.

For docker container registry/package artifactory, I use gitea. Gitea is very similar to Github. Before I found gitea, I used to use the public Dockerhub as my docker container registry. However, I want to keep the program logic private and gitea is the solution. As for a python package artifactory, it is now used to store a core python library which quite a number of other python programmes have a dependency one. The core python library contains reusable transport classes, like the connection to Dremio, connection to postgres, ingestion to Dremio etc. etc.



.. figure:: pics/Data_Platform_Architecture-ETL_Data_Ingestion.drawio.svg
   :alt: Data Ingestion

For data analytics, I ingest various data sources. I store them in the data lakehouse according to the Medallion Architecture (https://www.databricks.com/glossary/medallion-architecture). It basically means that data is stored in (i) raw form, (ii) cleaned/riched form and (iii) direclty consumable form by end users.

The framework I use for scraping the data online is scrapy, a battle-tested python framework with lots of built-in tools to help web-scraping, like auto-throttling, Item pipelines, csv exports. All these ingestion programmes run on Apache Airflow, which basically is a cron scheduler on stereoids (with a nice UI).





.. figure:: pics/Data_Platform_Architecture-ETL_Data_Distribution_Apps.drawio.svg
   :alt: Minio Main Page

   Minio

Data_Platform_Architecture-ETL_Data_Ingestion.drawio.svg

