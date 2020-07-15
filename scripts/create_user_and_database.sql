SELECT 'Creating database \'doctrine_game\'';

DROP DATABASE IF EXISTS doctrine_game;
CREATE DATABASE doctrine_game;


SELECT 'Creating user \'doctrine\' and granting privileges';

DROP USER IF EXISTS 'doctrine'@'localhost';
CREATE USER 'doctrine'@'localhost' IDENTIFIED BY 'doctrine';
GRANT ALL PRIVILEGES ON doctrine_game.* TO 'doctrine'@'localhost';
FLUSH PRIVILEGES;
