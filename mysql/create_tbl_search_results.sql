CREATE TABLE search_result_test IF NOT EXISTS(
    doc_number VARCHAR(1000),
    issue_date DATE,
    applicant_name VARCHAR(1000),
    inventor_name VARCHAR(1000),
    abstract_lang VARCHAR(1000),
    abstract TEXT,
    full_txt_exists VARCHAR(1000)
    );