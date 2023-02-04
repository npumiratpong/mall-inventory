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

show columns from roles;


### Create Mock Users
insert into users (username, hashed_password, first_name, last_name, email, created_when, modified_when, is_active)
values ('johndoe', '$2y$10$Oii4iPEwk8MIQ2wp0WOdq.7XGMneEUOMUtq6aj/lp7rPQnTJLZVZy', 'John', 'Doe', 'johndoe@example.com', now(), now(), True)

insert into users (username, hashed_password, first_name, last_name, email, created_when, modified_when, is_active)
values ('alice', '$2y$10$Oii4iPEwk8MIQ2wp0WOdq.7XGMneEUOMUtq6aj/lp7rPQnTJLZVZy', 'Alice', 'Johnson', 'alicejohnson@example.com', now(), now(), True)

insert into users (username, hashed_password, first_name, last_name, email, created_when, modified_when, is_active)
values ('jason', '$2y$10$Oii4iPEwk8MIQ2wp0WOdq.7XGMneEUOMUtq6aj/lp7rPQnTJLZVZy', 'jason', 'Johnson', 'jason@example.com', now(), now(), False)

insert into users (username, hashed_password, first_name, last_name, email, created_when, modified_when, is_active)
values ('elena', '$2y$10$Oii4iPEwk8MIQ2wp0WOdq.7XGMneEUOMUtq6aj/lp7rPQnTJLZVZy', 'Elena', 'Johnson', 'elena@example.com', now(), now(), True)

insert into users (username, hashed_password, first_name, last_name, email, created_when, modified_when, is_active)
values ('hector', '$2y$10$Oii4iPEwk8MIQ2wp0WOdq.7XGMneEUOMUtq6aj/lp7rPQnTJLZVZy', 'Hector', 'Johnson', 'hector@example.com', now(), now(), True)

insert into users (username, hashed_password, first_name, last_name, email, created_when, modified_when, is_active)
values ('william', '$2y$10$Oii4iPEwk8MIQ2wp0WOdq.7XGMneEUOMUtq6aj/lp7rPQnTJLZVZy', 'William', 'Johnson', 'william@example.com', now(), now(), True)



select * from users


## Master table for user (admin , user)
create table roles (
	role_id INT NOT NULL AUTO_INCREMENT,
	role_name VARCHAR(50) NOT NULL,
	PRIMARY KEY (role_id)
	
);

ALTER TABLE roles AUTO_INCREMENT = 1


#Create User Roles
insert into roles (role_name) values ('admin'), ('sale_store'), ('sale_admin_store'), ('sale_shopping_mall'), ('sale_admin_shopping_mall')

select * from roles 

delete from roles r 


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

#Create Mock User Mapping between role_id and user_id 
insert into user_mapping (user_id, role_id, created_when, modified_when) values (1, 1, NOW(), now())

insert into user_mapping (user_id, role_id, created_when, modified_when) values (2, 2, NOW(), now())

insert into user_mapping (user_id, role_id, created_when, modified_when) values (3, 1, NOW(), now())

insert into user_mapping (user_id, role_id, created_when, modified_when) values (4, 3, NOW(), now())

insert into user_mapping (user_id, role_id, created_when, modified_when) values (5, 4, NOW(), now())

insert into user_mapping (user_id, role_id, created_when, modified_when) values (6, 5, NOW(), now())


select * from user_mapping 

delete from user_mapping 


## Static table to store product list, inserted daily 
create table products (
	product_id  VARCHAR(50) NOT NULL,
	product_name  VARCHAR(255) NOT NULL,
	barcode VARCHAR(1000),
	created_when datetime NOT NULL,
	PRIMARY KEY(product_id, created_when)  
)

drop table products 

select * from products p 

delete from products 

ALTER TABLE products  MODIFY COLUMN product_id VARCHAR(50)

#insert Mock Product data
insert into products (product_id, product_name, barcode, created_when) values ('CEB-5005-A3', 'หนังสือ', '1111122222333', NOW()), ('BDW-5005-B4', 'ปากกา', '1111122222444', NOW()), ('ASC-5005-A3', 'ดินสอ', '1111122222555', NOW())

select * from products p 

## Master table for customer (Big C, Lotus) 
create table customers (
	customer_id INT NOT NULL AUTO_INCREMENT,
	customer_name VARCHAR(50) NOT NULL,
	PRIMARY KEY (customer_id)
	
);

select * from customers c 

drop table customers 

## Mapping table bwteen product and customer, show price for specific customer, Load data from CSV

create table product_price (
	product_id VARCHAR(50) NOT NULL, 
	customer_id int NOT NULL ,
	unit 	VARCHAR(20)  NULL,
	price  float NOT NULL,
	created_when datetime NOT NULL,
	PRIMARY KEY(product_id, customer_id),
	   FOREIGN KEY products(product_id)
       REFERENCES products(product_id),
       FOREIGN KEY (customer_id)
       REFERENCES customers(customer_id)
);

drop table product_price 

select * from product_price pp 


delete from products 

select * from products p

select count(*) from products p 