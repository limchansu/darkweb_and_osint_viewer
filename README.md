# Overview

This project is a **Dark Web and OSINT Data Monitoring System** that continuously collects, processes, and alerts critical information from various sources, such as darknet forums and OSINT feeds. By leveraging automation, the system integrates **web crawling**, **data analysis**, and **real-time monitoring**, storing the results in a **MongoDB database** and providing timely alerts via **email** and **Discord** notifications.

---

# Key Feature

- **Real-Time Data Collection**: The system employs multiple crawlers to collect data from OSINT and Dark Web leak sources, accessed via Tor (9050 proxy).
- **Database Management**: MongoDB serves as the central storage for all collected data, utilizing separate collections for each crawler source.
- **Change Monitoring**: DB streams monitor updates and trigger email or Discord alerts for timely notifications.
- **User Access**: A Flask web interface allows users to search and fetch the latest information stored in the database.
- **Scalable & Automated**: The entire system can be deployed and managed with Docker Compose, enabling seamless integration and execution.

---

# Notes

- **Data Segregation**: Collected data is stored in different collections depending on the crawler source.
- **Proxy Security**: Tor (9050) is used to access Dark Web sites securely and anonymously.
- **Alert System**: Real-time alerts are sent via email and Discord upon detecting DB updates or new entries.

---

# Guide For Operation



---

# Tech. Stack Info

- **Backend**: Python (Flask, asyncio)
- **Database**: MongoDB (Replica Set)
- **Web Crawling**: Playwright, BeautifulSoup
- **Proxy**: Tor (9050 SOCKS5)
- **Containerization**: Docker Compose
- **Alerts**: Email and Discord Integration
- **Frontend**: HTML (Flask templates)