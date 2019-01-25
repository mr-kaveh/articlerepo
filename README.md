# Article Repo
## Sample Flask Application for Viewing, Adding, Editing and Deleting Articles
#### installs mariadb

`$ sudo apt install mariadb-server libmysql-dev`


#### creates Database and Tables

`sql> create database myflaskapp;`

`sql> create table users(id int(11) auto_increment primary key,
				   name varchar(100),email varchar(50),
				   username varchar(30), password varchar(15), 
				   register_date timestamp default current_timestamp);`

`sql> create table articles (id init(11) auto_increment primary key, 
						title varchar(255), author varchar(100),
						body text, create_date timestamp default current_timestamp);`
