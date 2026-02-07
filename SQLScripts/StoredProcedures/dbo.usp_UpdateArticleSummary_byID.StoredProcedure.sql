CREATE OR ALTER PROCEDURE dbo.usp_UpdateArticleSummary_byID (
    @ArticleID INT = NULL  
    , @ArticleSummary NVARCHAR(MAX) = NULL
)
AS
BEGIN
    SET NOCOUNT ON;

    IF(@ArticleID IS NULL)
        BEGIN 
            RAISERROR('ERROR! ArticleID ISNULL', 16, 1)
            RETURN;
        END 
    
    IF(@ArticleSummary IS NULL)
        BEGIN 
            RAISERROR('ERROR! No Summary provided!', 16, 1)
            RETURN;

        END

    -- Update dbo.tbl_articles
    UPDATE T 
    SET T.GeneratedSummary = @ArticleSummary
    FROM dbo.tbl_articles T 
    WHERE T.ArticleID = @ArticleID

    IF @@ROWCOUNT = 0
        BEGIN 
            RAISERROR('Warning: No article found with that ArticleID. No rows updated.', 10, 1)
        END


     
END