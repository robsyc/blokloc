DROP database bldb;
CREATE database bldb;
USE bldb;

CREATE TABLE `location` (
	`id` INT PRIMARY KEY,
	`title` VARCHAR(128),
	`label` VARCHAR(128),
	`address` VARCHAR(255),
	`tot_cap` INT UNSIGNED,
	`tot_res` INT UNSIGNED,
	`latitude` DECIMAL(18,16),
	`longitude` DECIMAL(18,16),
	`teaser_img_url` VARCHAR(255),
	`more_info_url` VARCHAR(255),
	`t_open` TIME,
	`t_close` TIME,
	`avg_rating` FLOAT(5) CHECK (avg_rating >= 0 AND avg_rating <= 5),
	`avg_occupancy` FLOAT(5) CHECK (avg_occupancy >= 0 AND avg_occupancy <= 5),
	`avg_internet` FLOAT(5) CHECK (avg_internet >= 0 AND avg_internet <= 5)
);

CREATE TABLE `user` (
	`id` INT PRIMARY KEY,
	`name` VARCHAR(255),
	`ncomments` INT UNSIGNED,
	`avg_rating` FLOAT(5) CHECK (avg_rating >= 0 AND avg_rating <= 5),
	`avg_rated` FLOAT(5) CHECK (avg_rated >= 0 AND avg_rated <= 5)
);

CREATE TABLE `review` (
	`id` INT PRIMARY KEY,
	`user_id` INT,
	`loc_id` INT,
	`date` DATETIME,
	`avg_rating` FLOAT(5) CHECK (avg_rating >= 0 AND avg_rating <= 5)
);

CREATE TABLE `observation` (
	`id` INT PRIMARY KEY,
	`review_id` INT,
    `attribute` ENUM("obs_t_open", "obs_t_close", "obs_text", "obs_rating", "obs_occupancy", "obs_internet"),
    `input` VARCHAR(255)
);

CREATE TABLE `rating` (
	`id` INT PRIMARY KEY,
    `user_id` INT,
    `review_id` INT,
    `input` VARCHAR(255)
);

ALTER TABLE `review` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `review` ADD FOREIGN KEY (`loc_id`) REFERENCES `location` (`id`);
ALTER TABLE `observation` ADD FOREIGN KEY (`review_id`) REFERENCES `review` (`id`);
ALTER TABLE `rating` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `rating` ADD FOREIGN KEY (`review_id`) REFERENCES `review` (`id`);
CREATE INDEX `obs_attribute` ON observation (attribute);