IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[tbl_articles]') AND type in (N'U'))
BEGIN
    CREATE TABLE dbo.tbl_articles (
        -- Auto-incrementing unique integer ID (Primary Key)
        ArticleID INT IDENTITY(1,1) PRIMARY KEY, 
        
        -- Content Fields
        Title NVARCHAR(MAX),
        Description NVARCHAR(MAX),
        -- URL set to 900 to stay within index limits while ensuring uniqueness
        URL NVARCHAR(900) NOT NULL CONSTRAINT UC_Article_URL UNIQUE, 
        imageURL NVARCHAR(MAX),
        
        -- Metadata Fields
        Domain NVARCHAR(255),
        Country NVARCHAR(10),
        Language NVARCHAR(10),
        Medium NVARCHAR(50),
        
        -- Metrics and Dates
        PublishDate DATETIMEOFFSET, -- Best for "2025-12-19T15:33:12+08:00"
        Score FLOAT,
        SentimentPositive DECIMAL(10, 8),
        
        -- Audit column
        DateImported DATETIME DEFAULT GETDATE()
    );
    PRINT 'Table [dbo].[tbl_articles] created successfully.';
END
ELSE
BEGIN
    PRINT 'Table [dbo].[tbl_articles] already exists. Skipping creation.';
END
GO