CREATE DATABASE CompetitionManagementSystem;
GO

USE CompetitionManagementSystem;
GO

-- ==========================================
-- 1. TABLES CREATION (Design + Normalization)
-- ==========================================
CREATE TABLE Participants (
    ParticipantID INT PRIMARY KEY IDENTITY(1,1),
    FullName VARCHAR(100),
    Email VARCHAR(100) UNIQUE,
    Country VARCHAR(50)
);

CREATE TABLE Competitions (
    CompetitionID INT PRIMARY KEY IDENTITY(1,1),
    CompetitionName VARCHAR(100),
  //  Location VARCHAR(100),
    CompetitionDate DATE  //
);

CREATE TABLE Judges (
    JudgeID INT PRIMARY KEY IDENTITY(1,1),
    JudgeName VARCHAR(100)
);

CREATE TABLE Registrations (
    RegistrationID INT PRIMARY KEY IDENTITY(1,1),
    ParticipantID INT,
    CompetitionID INT,
    FOREIGN KEY (ParticipantID) REFERENCES Participants(ParticipantID),
    FOREIGN KEY (CompetitionID) REFERENCES Competitions(CompetitionID)
);

CREATE TABLE Rankings (
    CompetitionID INT,
    ParticipantID INT,
    TotalScore DECIMAL(10,2) DEFAULT 0,
    PRIMARY KEY (CompetitionID, ParticipantID),
    FOREIGN KEY (CompetitionID) REFERENCES Competitions(CompetitionID),
    FOREIGN KEY (ParticipantID) REFERENCES Participants(ParticipantID)
);

CREATE TABLE Scores (
    ScoreID INT PRIMARY KEY IDENTITY(1,1),
    ParticipantID INT,
    CompetitionID INT,
    JudgeID INT,
    ScoreValue DECIMAL(5,2),
    FOREIGN KEY (ParticipantID) REFERENCES Participants(ParticipantID),
    FOREIGN KEY (CompetitionID) REFERENCES Competitions(CompetitionID),
    FOREIGN KEY (JudgeID) REFERENCES Judges(JudgeID)
);
GO

-- ==========================================
-- 2. INSERT INITIAL DATA (Dummy Data)
-- ==========================================
INSERT INTO Participants (FullName, Email, Country) VALUES
('Ahmed Ali', 'ahmed@gmail.com', 'Egypt'),
('Sara Mohamed', 'sara@gmail.com', 'Egypt'),
('John Smith', 'john@gmail.com', 'USA'),
('Mostafa', 'mostafa@gmail.com', 'Egypt');

INSERT INTO Competitions (CompetitionName, Location, CompetitionDate) VALUES
('Programming Contest', 'Cairo', '2026-05-01'),
('Robotics Competition', 'Alexandria', '2026-06-15'),
('AI Hackathon', 'Giza', '2026-07-10');

INSERT INTO Judges (JudgeName) VALUES 
('Dr. Doaa Mohey Eldin'), 
('Dr. Sarah Naiem');

INSERT INTO Registrations (ParticipantID, CompetitionID) VALUES
(1,1), (2,1), (1,2), (3,3);
GO

-- ==========================================
-- 3. PROCEDURES & TRIGGERS
-- ==========================================

-- Stored Procedure for Score Submission
CREATE PROCEDURE SubmitScore
    @p_ParticipantID INT,
    @p_CompetitionID INT,
    @p_JudgeID INT,
    @p_ScoreValue DECIMAL(5,2)
AS
BEGIN
    INSERT INTO Scores (ParticipantID, CompetitionID, JudgeID, ScoreValue)
    VALUES (@p_ParticipantID, @p_CompetitionID, @p_JudgeID, @p_ScoreValue);
END;
GO

-- Trigger for Auto-Updating Rankings
CREATE TRIGGER trg_AutoUpdateRanking
ON Scores
AFTER INSERT
AS
BEGIN
    -- 1. Update existing ranking score
    UPDATE R
    SET R.TotalScore = R.TotalScore + i.ScoreValue
    FROM Rankings R
    INNER JOIN inserted i ON R.ParticipantID = i.ParticipantID AND R.CompetitionID = i.CompetitionID;

    -- 2. Insert new ranking if it doesn't exist
    INSERT INTO Rankings (CompetitionID, ParticipantID, TotalScore)
    SELECT i.CompetitionID, i.ParticipantID, i.ScoreValue
    FROM inserted i
    WHERE NOT EXISTS (
        SELECT 1 FROM Rankings R
        WHERE R.ParticipantID = i.ParticipantID AND R.CompetitionID = i.CompetitionID
    );
END;
GO

-- ==========================================
-- 4. REQUIRED QUERIES (JOINS, Aggregation, Projection, Subqueries)
-- ==========================================

-- Query 1: Projection & JOINs (عرض الترتيب المباشر)
SELECT 
    RANK() OVER (PARTITION BY R.CompetitionID ORDER BY R.TotalScore DESC) AS RankPosition,
    P.FullName AS Participant,
    C.CompetitionName,
    R.TotalScore
FROM Rankings R
INNER JOIN Participants P ON R.ParticipantID = P.ParticipantID
INNER JOIN Competitions C ON R.CompetitionID = C.CompetitionID;

-- Query 2: Aggregation & JOINs (عدد المشتركين في كل مسابقة)
SELECT 
    C.CompetitionName, 
    COUNT(R.ParticipantID) AS NumberOfParticipants
FROM Competitions C
LEFT JOIN Registrations R ON C.CompetitionID = R.CompetitionID
GROUP BY C.CompetitionName;

-- Query 3: Subqueries (معرفة المتسابقين اللي متسجلوش في أي مسابقة حتى الآن)
SELECT 
    ParticipantID, 
    FullName, 
    Email
FROM Participants
WHERE ParticipantID NOT IN (SELECT ParticipantID FROM Registrations);
GO