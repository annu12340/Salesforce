# Salesforce Customer Support System

This project consists of two main components:

1. **Customer Facing App (React)**
   - Frontend: React-based web application
   - Backend: Node.js/Express API
   - Location: `/customer-app`

2. **Employee Facing App (Python Slack Bot)**
   - Python-based Slack bot for employee support
   - Uses Slack Bolt SDK
   - Location: `/employee-bot`

## Setup Instructions

### Customer Facing App
```bash
cd customer-app
npm install
npm run dev
```

### Employee Facing App
```bash
cd employee-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Environment Variables

Both applications require environment variables to be set up. Please refer to the respective `.env.example` files in each directory for required variables.