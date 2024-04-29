CREATE TABLE Users (
    SpotifyUserID VARCHAR(255) PRIMARY KEY,
    Access_Token VARCHAR(255)   -- not necessary
);

CREATE TABLE Pin (
    Pin_ID INT AUTO_INCREMENT PRIMARY KEY,
    User_ID VARCHAR(255),
    Name TEXT,
    Latitude DOUBLE,
    Longitude DOUBLE,
    -- Priority INT,
    Radius DOUBLE,
    -- DateCreated DATETIME,
    URI VARCHAR(255),  
    FOREIGN KEY (UserID) REFERENCES Users(SpotifyUserID)
);