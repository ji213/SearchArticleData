CREATE OR ALTER PROCEDURE dbo.usp_GetUnsummarizedArticle_byID (
    @ArticleID INT = NULL  
)
AS
BEGIN
    SET NOCOUNT ON;

    -- This is only for debugging purposes, so we will always pass in a parameter
    
    SELECT TOP 1 ArticleID, URL, Title, Domain, Language
    FROM dbo.tbl_articles
    WHERE GeneratedSummary IS NULL
      -- If @ArticleID is provided, filter by it; otherwise, ignore this filter
    AND ArticleID = @ArticleID
    ORDER BY ArticleID ASC; 
END