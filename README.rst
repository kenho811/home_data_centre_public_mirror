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

.. figure:: pics/Data_Platform_Architecture-ETL_Data_Distribution_Apps.drawio.svg
   :alt: Minio Main Page

   Minio



