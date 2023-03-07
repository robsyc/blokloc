CREATE TABLE `locations` (
  `id` INT PRIMARY KEY,
  `title` VARCHAR(128),
  `label` VARCHAR(128),
  `address` VARCHAR(255),
  `tot_cap` INT UNSIGNED,
  `tot_res` INT UNSIGNED,
  `t_open` TIME,
  `t_close` TIME,
  `latitude` DECIMAL(18,16),
  `longitude` DECIMAL(18,16),
  `teaser_img_url` VARCHAR(255),
  `more_info_url` VARCHAR(255),
  `input_general` FLOAT(5) CHECK (input_general >= 0 AND input_general <= 5),
  `input_occupancy` FLOAT(5) CHECK (input_occupancy >= 0 AND input_occupancy <= 3),
  `input_internet` FLOAT(5) CHECK (input_internet >= 0 AND input_internet <= 3),
  `input_electr` FLOAT(5) CHECK (input_electr >= 0 AND input_electr <= 3)
  );

CREATE TABLE `users` (
  `id` INT PRIMARY KEY,
  `name` VARCHAR(255),
  `ncomments` INT UNSIGNED,
  `input_score` FLOAT(5) DEFAULT 0.5 CHECK (avg_rating >= 0 AND avg_rating <= 1),
  `avg_rating` FLOAT(5) CHECK (avg_rating >= 0 AND avg_rating <= 5),
  `avg_comment_rating` FLOAT(5) CHECK (avg_comment_rating >= 0 AND avg_comment_rating <= 5)
);

CREATE TABLE `reviews` (
  `id` INT PRIMARY KEY,
  `user_id` INT,
  `loc_id` INT,
  `date` DATETIME,
  `input_text` TEXT,
  `input_general` ENUM("x-sad", "sad", "neutral", "happy", "x-happy"),
  `input_occupancy` ENUM("sad", "neutral", "happy"),
  `input_internet` ENUM("sad", "neutral", "happy"),
  `input_electr` ENUM("sad", "neutral", "happy"),
  `comment_rating` FLOAT(5) CHECK (comment_rating >= 0 AND comment_rating <= 5)
);

ALTER TABLE `comments` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
ALTER TABLE `comments` ADD FOREIGN KEY (`loc_id`) REFERENCES `locations` (`id`);