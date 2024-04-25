CREATE TABLE Users (
    SpotifyUserID VARCHAR(255) PRIMARY KEY,
    Access_Token VARCHAR(255)   -- not necessary
);

CREATE TABLE Pin (
    Pin_ID INT AUTO_INCREMENT PRIMARY KEY,
    UserID VARCHAR(255),
    Location TEXT,
    Latitude DOUBLE,
    Longitude DOUBLE,
    Radius DOUBLE,
    -- Priority INT,
    PlaylistID INT,
    -- DateCreated DATETIME,
    FOREIGN KEY (UserID) REFERENCES Users(SpotifyUserID),
    -- FOREIGN KEY (PlaylistID) REFERENCES Playlist(Playlist_ID)
);
