## NOTE : recommned collation is utf8_unicode_ci
## Master table for user 
create table users(
	user_id INT   NOT NULL  AUTO_INCREMENT,
	username VARCHAR(50) NOT NULL,
	hashed_password VARCHAR(255) NOT NULL,
	first_name VARCHAR(255) NOT NULL,
	last_name VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	created_when datetime NOT NULL,
	modified_when datetime,
	is_active BOOL NOT NULL,
	PRIMARY KEY (user_id)
);


## Master table for user (admin , user)
create table roles (
	role_id INT NOT NULL AUTO_INCREMENT,
	role_name VARCHAR(50) NOT NULL,
	PRIMARY KEY (role_id)
	
);

## Mapping between user and roles 
create table user_mapping (
	user_id int NOT NULL , 
	role_id int NOT NULL ,
	created_when datetime NOT NULL,
	modified_when datetime not null,
	PRIMARY KEY(user_id),
	   FOREIGN KEY (user_id)
       		REFERENCES users(user_id),
       FOREIGN KEY (role_id)
       		REFERENCES roles(role_id)
);


## Static table to store product list, inserted daily 
create table products (
	product_id  INT  NOT NULL AUTO_INCREMENT,
	product_name  VARCHAR(255) NOT NULL,
	barcode VARCHAR(1000),
	created_when datetime NOT NULL,
	PRIMARY KEY(product_id,created_when)  
)

## Master table for customer (Big C, Lotus) 
create table customers (
	customer_id INT NOT NULL AUTO_INCREMENT,
	customer_name VARCHAR(50) NOT NULL,
	PRIMARY KEY (customer_id)
	
);

## Mapping table bwteen product and customer, show price for specific customer, Load data from CSV
create table product_price (
	product_id int NOT NULL , 
	customer_id int NOT NULL ,
	unite 	VARCHAR(20)  NULL,
	price  float NOT NULL,
	created_when datetime NOT NULL,
	PRIMARY KEY(product_id,customer_id),
	   FOREIGN KEY products(product_id)
       REFERENCES products(product_id),
       FOREIGN KEY (customer_id)
       REFERENCES customers(customer_id)
);







