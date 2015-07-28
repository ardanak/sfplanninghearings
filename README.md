# SF PLANNING HEARINGS

Provides up to date hearing information regarding proposed building projects set forth by the San Francisco Housing Planning Commission. All data is stored in an elasticsearch instance and supports a full text search on notice announcements. It features an api based on the python restless framework to provide http access to the data.

#Setup

Install elasticsearch

https://www.elastic.co/guide/en/elasticsearch/reference/1.6/setup.html

git clone https://github.com/ardanak/sfplanninghearings.git

cd sfplanninghearings

run the following command:

sudo pip install -r requirements.txt

It may be necessary to install elasticsearch-dsl separately using the following command

sudo pip install git+git://github.com/elastic/elasticsearch-dsl-py.git@master


#Initialize database

python app_init.py

To set up automatic updates to database

Use the command:

crontab -e

add the line:

0 5 * * 5 python /PATH-TO-FILE/app.py

#Deploy Api app

run the following:

python api.py

or run it in the background:

python api.py &

*Note: Api server authentication is currently not implemented.

#Usage

Cases are stored using the case id (including the case code) as the index id.
Case id is stored without dots or dashes.
However, '!' and '_' is allowed.

For example'
2015-003493CUA is stored as 2015003493CUA
and can be queried with

http://YOUR_URL/api/cases/2015003493CUA

Notices are not indexed with a natural language key.
Queries are implemented with a search on the database.

For example'
Notices related to case id 2015-003493CUA
can be queried using

http://YOUR_URL/api/notices/?q=case_num:2015003493

The case code (CUA) needs to be ommitted for all queries on .../api/notices

A single case can have multiple codes and may be stored as separate entries.

#More on queries

http://YOUR_URL/api/cases

and

http://YOUR_URL/api/notices

returns all case and notice data respectively.
All queries return a maximum of 20 results by default.

To get a different number of results, add /?limit=VALUE to any query
