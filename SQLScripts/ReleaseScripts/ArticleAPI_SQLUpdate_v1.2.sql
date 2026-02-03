-- SQL Script for all database modifications made in this release

IF NOT EXISTS (
    SELECT 1 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('dbo.tbl_articles') 
    AND name = 'GeneratedSummary'
)
BEGIN
    ALTER TABLE dbo.tbl_articles 
    ADD GeneratedSummary NVARCHAR(MAX) NULL;
    
    PRINT 'Column GeneratedSummary added successfully.';
END
ELSE
BEGIN
    PRINT 'Column GeneratedSummary already exists. Skipping...';
END