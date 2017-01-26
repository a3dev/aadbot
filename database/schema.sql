CREATE TABLE "commentReplies" (
  "id" VARCHAR PRIMARY KEY NOT NULL,
  "subreddit" TEXT NOT NULL,
  "context" TEXT NOT NULL,
  "body" TEXT NOT NULL,
  "author" VARCHAR NOT NULL
);

CREATE TABLE "commentReplies_log" (
  "id" VARCHAR PRIMARY KEY NOT NULL,
  "processed" BOOL NOT NULL  DEFAULT 0,
  "isCommand" BOOL NOT NULL  DEFAULT 0,
  "isCompliment" BOOL NOT NULL  DEFAULT 0,
  "Failed" BOOL NOT NULL  DEFAULT 1
);

CREATE TABLE "domains" (
  "domain" VARCHAR NOT NULL,
  "blacklisted" BOOL NOT NULL  DEFAULT 0
);

CREATE TABLE "privateMessages_log" (
  "id" VARCHAR PRIMARY KEY  NOT NULL  UNIQUE,
  "processed" BOOL NOT NULL  DEFAULT 0,
  "isBot" BOOL NOT NULL  DEFAULT 0,
  "failed" BOOL NOT NULL  DEFAULT 1
);

CREATE TABLE "privateMessages" (
  "id" VARCHAR PRIMARY KEY  NOT NULL  UNIQUE,
  "subject" TEXT NOT NULL,
  "body" TEXT NOT NULL,
  "author" VARCHAR NOT NULL
);

CREATE TABLE "submissions" (
  "id" VARCHAR PRIMARY KEY  NOT NULL  UNIQUE,
  "url" TEXT NOT NULL,
  "title" TEXT NOT NULL,
  "created_utc" DOUBLE NOT NULL,
  "author" VARCHAR NOT NULL
);

CREATE TABLE "submissions_log" (
  "id" VARCHAR PRIMARY KEY  NOT NULL  UNIQUE,
  "processed" BOOL NOT NULL  DEFAULT 0,
  "failed" BOOL NOT NULL  DEFAULT 1
);

CREATE TABLE "ignoredUsers" (
  "username" VARCHAR PRIMARY KEY  NOT NULL  UNIQUE
);

CREATE TABLE "subreddit_list" (
  "subName" VARCHAR PRIMARY KEY  NOT NULL  UNIQUE
);

INSERT INTO domains (domain, blacklisted) VALUES
  ("indiatimes.com", 0),
  ("intoday.in", 0),
  ("ndtv.com", 0),
  ("indianexpress.com", 0),
  ("hindustantimes.com", 0),
  ("livemint.com", 0),
  ("mid-day.com", 0),
  ("business-standard.com", 0),
  ("financialexpress.com", 0);

INSERT INTO subreddit_list (subName) VALUES
  ("testsleep");
