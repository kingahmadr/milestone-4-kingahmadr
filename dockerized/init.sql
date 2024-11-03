-- Create database
CREATE DATABASE IF NOT EXISTS `production`;
USE `production`;

-- Create table reviews
CREATE TABLE `reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product` varchar(50) NOT NULL,
  `rating` int NOT NULL,
  `is_deleted` boolean NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
);

-- Create table users
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `email` varchar(50) NOT NULL,
  `password_hash` text NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_username` (`username`)
);

-- Create table roles
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `slug` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `ix_roles_name` (`name`)
);

-- Create table user_roles
CREATE TABLE `user_roles` (
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
);
-- Insert predefined roles
INSERT INTO `roles` (`name`, `slug`)
VALUES
    ('Administrator', 'admin'),
    ('User', 'user');

-- Insert predefined reviews

INSERT INTO `reviews` (`product`,`rating`,`description`,`is_deleted`)
VALUES
    ('Fan', 4, 'Good to cooling the environments',0),
    ('Laptop', 5, 'Good performance for slightly mobile activity',0),
    ('Smartphone', 4.5, 'Good Perfomance for mobile activity',0),
    ('PC', 5, 'Good Performance to code',0),
    ('Lamp', 1, 'Nothing good',0);
