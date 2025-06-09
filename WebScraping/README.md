# 💼 Web Scraping for Counter-Financing-Terrorism AML Solution

A complete Anti-Money Laundering (AML) and Counter-Financing of Terrorism (CFT) system that automates the collection, processing, and analysis of sanction and PEP data using **Web Scraping** and a **FastAPI** service for smooth scheduling and integration of processes.

---

## 🚀 Project Modules

### 🕸️ Web Scraping Module

Scrapes data from official sanctions and PEP (Politically Exposed Persons) sources, normalizes it, and stores it in structured format.

#### Features:
- Automated scraping with pagination handling
- Structured output: Name, DOB, Country, Gender, Other names, Source URL, etc.
- Supports multiple sources

### 🛠 Technologies Used
- Python 3.8+
- BeautifulSoup4, Requests, Pandas – for web scraping
- FastAPI, Uvicorn – for API development
- MongoDB – for persistent data storage

### ⏰ Scheduled Web Scraping
This project supports automated web scraping every day at midnight using APScheduler.
A script (scheduler.py) is configured to run all scraping jobs automatically at midnight daily.
