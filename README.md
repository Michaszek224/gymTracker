# Gym Tracker API

A simple API built using Flask to track gym activities. This project integrates with Supabase for database management and uses environment variables to securely store sensitive information.

## Features

- Basic API with a home route returning a message.
- Integration with Supabase for data storage.
- Secure handling of API keys and URLs using environment variables.

## Setup

### Requirements

- Python 3.7+
- Flask
- python-dotenv
- supabase-py

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Michaszek224/gymTracker.git
   cd gym-tracker-api

2. **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt


4. **Set up environment variables:**
    ```bash
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_key

### Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

### License
This project is licensed under the MIT License.
