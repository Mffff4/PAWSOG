# PAWS Bot

[![Bot Link](https://img.shields.io/badge/Telegram_Bot-Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/pawsbot/start?startapp=bro-228618799)
[![Channel Link](https://img.shields.io/badge/Telegram_Channel-Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+Ayp1HeUYsjdmZjgy)
[![Channel Link](https://img.shields.io/badge/Bot_Collection-Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+uF4lQD9ZEUE4NGUy)

---

## 📑 Table of Contents
1. [Description](#description)
2. [Key Features](#key-features)
3. [Installation](#installation)
   - [Quick Start](#quick-start)
   - [Manual Installation](#manual-installation)
4. [Settings](#settings)
5. [Support and Donations](#support-and-donations)
6. [Contact](#contact)

---

## 📜 Description
**PAWS Bot** is a powerful bot for Telegram that helps automate interaction with the PAWS bot. It supports multithreading, proxy integration, and session creation via QR codes.

---

## 🌟 Key Features
- 🔄 **Multithreading** — supports parallel processes to increase work speed
- 🔐 **Proxy binding to session** — allows secure work through proxy servers
- 📲 **Auto-account registration** — quick account registration via referral links
- 🎁 **Quest automation** — automatic completion and collection of quest rewards
- 📸 **Session creation via QR code** — fast and convenient session generation through a mobile app
- 📄 **Support for pyrogram session format (.session)** — easy integration with the Telegram API for session storage

---

## 🛠️ Installation

### Quick Start
1. **Download the project:**
   ```bash
   git clone https://github.com/Mffff4/PAWSOG.git
   cd PAWSOG
   ```

2. **Install dependencies:**
   - **Windows**:
     ```bash
     run.bat
     ```
   - **Linux**:
     ```bash
     run.sh
     ```

3. **Get API keys:**
   - Go to [my.telegram.org](https://my.telegram.org) and get your `API_ID` and `API_HASH`
   - Add this information to the `.env` file

4. **Run the bot:**
   ```bash
   python3 main.py --action 3  # Run the bot
   ```

### Manual Installation
1. **Linux:**
   ```bash
   sudo sh install.sh
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   cp .env-example .env
   nano .env  # Add your API_ID and API_HASH
   python3 main.py
   ```

2. **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env-example .env
   python main.py
   ```

---

## ⚙️ Settings

| Setting                    | Default Value          | Description                                                                  |
|---------------------------|------------------------|------------------------------------------------------------------------------|
| **API_ID**                |                        | Unique application ID required for Telegram API                              |
| **API_HASH**              |                        | Application hash used for Telegram API authentication                        |
| **USE_PROXY_FROM_FILE**   | False                  | Use proxy from bot/config/proxies.txt file                                  |
| **REF_ID**                | "MevXkpYU"            | Referral code for registering new users                                     |
| **REQUEST_TIMEOUT**       | [30, 60]              | Minimum and maximum timeout for HTTP requests in seconds                     |
| **RETRY_DELAY**           | [3, 10]               | Minimum and maximum delay between retry attempts in seconds                  |
| **MAX_RETRIES**           | 5                     | Maximum number of request retry attempts                                     |
| **ENABLE_QUESTS**         | True                  | Enable/disable automatic quest completion                                    |
| **QUEST_CHECK_INTERVAL**  | [300, 900]            | Minimum and maximum interval for checking new quests in seconds (5-15 min)   |
| **DELAY_BETWEEN_QUESTS**  | [3, 15]               | Minimum and maximum delay between quest completions in seconds               |
| **SERVER_CHECK_INTERVAL** | [240, 360]            | Minimum and maximum interval for server availability checks (4-6 min)        |
| **SERVER_CHECK_TIMEOUT**  | 5                     | Timeout for server availability check in seconds                             |
| **MAX_SERVER_CHECK_ATTEMPTS** | 3                 | Maximum number of server check attempts before sleep                         |
| **SERVER_CHECK_RETRY_DELAY** | [5, 15]            | Minimum and maximum delay between server check attempts in seconds           |
| **SLEEP_ON_SERVER_ERROR** | [240, 360]            | Minimum and maximum sleep duration on server error (4-6 min)                 |
| **SLEEP_AFTER_SESSIONS**  | [18000, 25200]        | Minimum and maximum sleep duration after processing all sessions (5-7 hours) |
| **LOGGING_LEVEL**         | "INFO"                | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)                        |
| **ENABLE_RICH_LOGGING**   | True                  | Enable enhanced console logging with rich formatting                         |
| **DETAILED_LOGGING**      | False                 | Enable detailed logging of operations                                        |
| **LOG_AUTH_DATA**         | False                 | Enable logging of authentication data                                        |
| **LOG_RESPONSE_DATA**     | False                 | Enable logging of server responses                                           |
| **LOG_REQUEST_DATA**      | False                 | Enable logging of request data                                               |
| **LOG_USER_AGENT**        | True                  | Enable logging of User-Agent information                                     |
| **LOG_PROXY**             | True                  | Enable logging of proxy information                                          |
---

## 💰 Support and Donations

Support the development using cryptocurrencies:

| Currency              | Wallet Address                                                                     |
|----------------------|------------------------------------------------------------------------------------|
| Bitcoin (BTC)|bc1qt84nyhuzcnkh2qpva93jdqa20hp49edcl94nf6| 
| Ethereum (ETH)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
|TON|UQBlvCgM84ijBQn0-PVP3On0fFVWds5SOHilxbe33EDQgryz|
| Binance Coin (BNB)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Solana (SOL)|3vVxkGKasJWCgoamdJiRPy6is4di72xR98CDj2UdS1BE| 
| Ripple (XRP)|rPJzfBcU6B8SYU5M8h36zuPcLCgRcpKNB4| 
| Dogecoin (DOGE)|DST5W1c4FFzHVhruVsa2zE6jh5dznLDkmW| 
| Polkadot (DOT)|1US84xhUghAhrMtw2bcZh9CXN3i7T1VJB2Gdjy9hNjR3K71| 
| Litecoin (LTC)|ltc1qcg8qesg8j4wvk9m7e74pm7aanl34y7q9rutvwu| 
| Matic|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Tron (TRX)|TQkDWCjchCLhNsGwr4YocUHEeezsB4jVo5| 

---

## 📞 Contact

If you have any questions or suggestions:
- **Telegram**: [Join our channel](https://t.me/+ap1Yd23CiuVkOTEy)

---

## ⚠️ Disclaimer

This software is provided "as is" without any warranties of any kind. By using this bot, you accept full responsibility for its use and any consequences that may arise.

The author is not responsible for:
- Any direct or indirect damages related to the use of the bot
- Possible violations of third-party service terms of use
- Account blocking or access restrictions

Use the bot at your own risk and in compliance with applicable laws and third-party service terms of use.

