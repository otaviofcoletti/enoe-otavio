CREATE TABLE IF NOT EXISTS ultrassonic (
    epoch VARCHAR(30) PRIMARY KEY,
    distance_cm VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS images (
    epoch VARCHAR(30) PRIMARY KEY,
    image_path VARCHAR(120) NOT NULL
);


CREATE TABLE IF NOT EXISTS raspberry_info (
    epoch VARCHAR(30) PRIMARY KEY,
    cpu_temperature FLOAT NOT NULL,
    cpu_usage FLOAT NOT NULL,
    ram_usage FLOAT NOT NULL,
    storage_usage FLOAT NOT NULL
);
