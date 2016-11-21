-- Adminer 4.2.5 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP TABLE IF EXISTS `error_cause`;
CREATE TABLE `error_cause` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `error_cause` (`id`, `name`, `description`) VALUES
(1,	'ERROR_MISSING_REQUIRED_OPTION',	'The service introduced new required option, which is not set for this mapping.'),
(2,	'ERROR_SERVICE_UNAVAILABLE',	'The service cannot be activated, because the remote probe does not provide it anymore.');

DROP TABLE IF EXISTS `mapped_services`;
CREATE TABLE `mapped_services` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `probe_service_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `status_id` int(11) NOT NULL DEFAULT '1',
  `error_cause_id` int(11) DEFAULT NULL,
  `current_status` int(11) DEFAULT NULL,
  `current_status_from` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `probe_service_id_name` (`probe_service_id`,`name`),
  KEY `status` (`status_id`),
  KEY `error_cause_id` (`error_cause_id`),
  KEY `current_status` (`current_status`),
  CONSTRAINT `mapped_services_ibfk_1` FOREIGN KEY (`probe_service_id`) REFERENCES `probe_services` (`id`) ON DELETE CASCADE,
  CONSTRAINT `mapped_services_ibfk_2` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`),
  CONSTRAINT `mapped_services_ibfk_3` FOREIGN KEY (`error_cause_id`) REFERENCES `error_cause` (`id`),
  CONSTRAINT `mapped_services_ibfk_4` FOREIGN KEY (`current_status`) REFERENCES `service_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `mapped_service_options`;
CREATE TABLE `mapped_service_options` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mapped_service_id` int(11) NOT NULL,
  `option_id` int(11) NOT NULL,
  `value` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mapped_service_id_option_id` (`mapped_service_id`,`option_id`),
  KEY `option_id` (`option_id`),
  CONSTRAINT `mapped_service_options_ibfk_1` FOREIGN KEY (`mapped_service_id`) REFERENCES `mapped_services` (`id`) ON DELETE CASCADE,
  CONSTRAINT `mapped_service_options_ibfk_2` FOREIGN KEY (`option_id`) REFERENCES `probe_service_options` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `probes`;
CREATE TABLE `probes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `probe_services`;
CREATE TABLE `probe_services` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `probe_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `deleted` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `probe_id_name` (`probe_id`,`name`),
  CONSTRAINT `probe_services_ibfk_1` FOREIGN KEY (`probe_id`) REFERENCES `probes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `probe_service_options`;
CREATE TABLE `probe_service_options` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `probe_service_id` int(11) NOT NULL,
  `identifier` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `data_type` enum('string','integer','double','bool','list') NOT NULL,
  `required` tinyint(1) NOT NULL DEFAULT '0',
  `description` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `probe_service_id_name` (`probe_service_id`,`name`),
  CONSTRAINT `probe_service_options_ibfk_1` FOREIGN KEY (`probe_service_id`) REFERENCES `probe_services` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `readings`;
CREATE TABLE `readings` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `mapped_service_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mapped_service_id` (`mapped_service_id`),
  CONSTRAINT `readings_ibfk_1` FOREIGN KEY (`mapped_service_id`) REFERENCES `mapped_services` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `reading_values`;
CREATE TABLE `reading_values` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `reading` int(10) unsigned NOT NULL,
  `datetime` datetime NOT NULL,
  `value` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `reading` (`reading`)
) ENGINE=TokuDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `service_status`;
CREATE TABLE `service_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `service_status` (`id`, `name`) VALUES
(1,	'ok'),
(2,	'warning'),
(3,	'error'),
(4,	'critical');

DROP TABLE IF EXISTS `service_status_history`;
CREATE TABLE `service_status_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mapped_service_id` int(11) NOT NULL,
  `service_status_id` int(11) DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mapped_service_id` (`mapped_service_id`),
  KEY `service_status_id` (`service_status_id`),
  CONSTRAINT `service_status_history_ibfk_1` FOREIGN KEY (`mapped_service_id`) REFERENCES `mapped_services` (`id`) ON DELETE CASCADE,
  CONSTRAINT `service_status_history_ibfk_2` FOREIGN KEY (`service_status_id`) REFERENCES `service_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `service_thresholds`;
CREATE TABLE `service_thresholds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `probe_service_id` int(11) NOT NULL,
  `service_status_id` int(11) NOT NULL,
  `reading` varchar(255) DEFAULT NULL,
  `min` bigint(20) NOT NULL,
  `max` bigint(20) NOT NULL,
  `source` enum('service','configuration') NOT NULL DEFAULT 'service',
  PRIMARY KEY (`id`),
  KEY `probe_service_id` (`probe_service_id`),
  KEY `service_status_id` (`service_status_id`),
  CONSTRAINT `service_thresholds_ibfk_1` FOREIGN KEY (`probe_service_id`) REFERENCES `probe_services` (`id`) ON DELETE CASCADE,
  CONSTRAINT `service_thresholds_ibfk_2` FOREIGN KEY (`service_status_id`) REFERENCES `service_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `status`;
CREATE TABLE `status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `status` (`id`, `name`) VALUES
(1,	'active'),
(2,	'suspended'),
(3,	'error');

-- 2016-11-21 08:15:28
