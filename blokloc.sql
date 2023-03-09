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
	`n_ratings` INT UNSIGNED,
	`tot_rated` INT UNSIGNED,
	`n_occupancy` INT UNSIGNED,
	`tot_occupancy` INT UNSIGNED,
	`n_internet` INT UNSIGNED,
	`tot_internet` INT UNSIGNED
);

CREATE TABLE `user` (
	`id` INT PRIMARY KEY,
	`name` VARCHAR(255),
	`n_reviews` INT UNSIGNED,
	`tot_rating` INT UNSIGNED,
    `n_ratings` INT UNSIGNED,
	`tot_rated` INT UNSIGNED
);

CREATE TABLE `review` (
	`id` INT PRIMARY KEY,
	`user_id` INT,
	`loc_id` INT,
	`date` DATETIME,
    `n_ratings` INT UNSIGNED,
	`tot_rated` INT UNSIGNED
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
    `input` ENUM("xsad", "sad", "neutral", "happy", "xhappy")
);

ALTER TABLE `review` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `review` ADD FOREIGN KEY (`loc_id`) REFERENCES `location` (`id`);
ALTER TABLE `observation` ADD FOREIGN KEY (`review_id`) REFERENCES `review` (`id`);
ALTER TABLE `rating` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
ALTER TABLE `rating` ADD FOREIGN KEY (`review_id`) REFERENCES `review` (`id`);
CREATE INDEX `obs_attribute` ON observation (attribute);