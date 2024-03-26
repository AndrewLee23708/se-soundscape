-- User Table
CREATE TABLE Users (
    SpotifyUserID VARCHAR(255) PRIMARY KEY,
    Access_Token VARCHAR(255)
);

-- Scape Table
CREATE TABLE Scape (
    Scape_ID INT AUTO_INCREMENT PRIMARY KEY,
    UserID VARCHAR(255),
    ScapeName VARCHAR(255),
    VisibilityStatus VARCHAR(50),
    ShareableLink TEXT,
    DateCreated DATETIME,
    FOREIGN KEY (UserID) REFERENCES User(SpotifyUserID)
);

-- Playlist Table
CREATE TABLE Playlist (
    Playlist_ID INT AUTO_INCREMENT PRIMARY KEY,
    Spotify_PlaylistID VARCHAR(255),
    DateCreated DATETIME
);

-- Pin Table
CREATE TABLE Pin (
    Pin_ID INT AUTO_INCREMENT PRIMARY KEY,
    ScapeID INT,
    Location TEXT,
    Latitude DOUBLE,
    Longitude DOUBLE,
    Radius DOUBLE,
    Priority INT,
    PlaylistID INT,
    DateCreated DATETIME,
    FOREIGN KEY (ScapeID) REFERENCES Scape(Scape_ID),
    FOREIGN KEY (PlaylistID) REFERENCES Playlist(Playlist_ID)
);

-- SharedScape Table
CREATE TABLE SharedScape (
    SharedScape_ID INT AUTO_INCREMENT PRIMARY KEY,
    ScapeID INT,
    SharedToUserID VARCHAR(255),
    FOREIGN KEY (ScapeID) REFERENCES Scape(Scape_ID),
    FOREIGN KEY (SharedToUserID) REFERENCES User(SpotifyUserID)
);
