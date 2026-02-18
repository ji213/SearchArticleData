CREATE OR ALTER PROCEDURE dbo.usp_GetUnsummarizedArticle
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Pick the oldest article that hasn't been summarized yet
    SELECT TOP 1 ArticleID, URL, Title, Domain, Language
    FROM dbo.tbl_articles
    WHERE GeneratedSummary IS NULL
    ORDER BY ArticleID ASC; 
END