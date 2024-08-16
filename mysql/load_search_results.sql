LOAD DATA INFILE '/var/lib/mysql-files/search_results_20210101_20210101.csv' 
INTO TABLE search_result_test 
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n';