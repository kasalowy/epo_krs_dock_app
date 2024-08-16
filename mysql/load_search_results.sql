LOAD DATA INFILE '/var/lib/mysql-files/search_results.csv' 
INTO TABLE db_test.search_result_test 
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n';