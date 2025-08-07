<p align="center">Bachelor Degree Thesis of<br>👨‍💻Muhammad Yusuf Ramadhan<br>BINUS University - Computer Science</p>

# 📊 Crypto Asset Automated Report Generator System

An automated report generation system built with Flask and Python to help crypto asset trading platforms comply with **OJK regulations (SEOJK 20/SEOJK.07/2024)** by generating accurate, timely, and regulation-compliant reports.

---

## 🚀 Features

- 🔄 **Automated Data Processing**: Uses ETL (Extract, Transform, Load) techniques to handle crypto transaction data
- 📄 **Report Generation**: Automatically creates daily and monthly reports in Excel format as required by OJK
- ✅ **Regulatory Compliance**: Adheres to SEOJK 20/SEOJK.07/2024 and POJK 27/2024 for digital asset trading
- 🛠 **Rule-Based Automation**: Implements rule-based logic to ensure accurate and consistent reporting
- 🔐 **User Authentication**: Secure login system with bcrypt password hashing
- 📊 **Data Management**: Complete database models for assets, customers, transactions, wallets, and holdings
- 🌱 **Data Seeding**: Includes seed data scripts for testing and development

---

## 🧰 Tech Stack

- **Backend**: Flask 3.1.0 (Python)
- **Database**: SQLite3 with SQLAlchemy ORM
- **Authentication**: Flask-Login & Flask-Bcrypt
- **Forms**: Flask-WTF
- **Data Processing**: Pandas & NumPy
- **Report Generation**: OpenPyXL for Excel file manipulation
- **Database Migrations**: Flask-Migrate (Alembic)
- **Frontend**: Bootstrap 4, jQuery
- **Containerization**: Docker

---

## 📁 Project Structure

```
ojk-crypto/
├── app/                        # Main application directory
│   ├── models.py              # Database models
│   ├── forms.py               # WTForms for user input
│   ├── routes/                # Route handlers
│   │   ├── auth.py           # Authentication routes
│   │   ├── daily.py          # Daily report generation
│   │   ├── monthly.py        # Monthly report generation
│   │   └── settings.py       # Application settings
│   ├── scripts/              # Utility scripts
│   │   ├── create_user.py    # User creation script
│   │   ├── populate_assets.py # Data population script
│   │   └── seeds/            # CSV seed data files
│   ├── static/               # Static assets
│   │   ├── daily_template.xlsx   # Daily report template
│   │   └── monthly_template.xlsx # Monthly report template
│   ├── templates/            # HTML templates
│   └── utils/                # Utility modules
│       ├── daily_report_generator.py
│       └── monthly_report_generator.py
├── migrations/               # Database migrations
├── instance/                 # Instance-specific files
│   └── app.db               # SQLite database
├── requirements.txt          # Python dependencies
├── config.py                # Configuration settings
├── run.py                   # Application entry point
└── Dockerfile               # Docker configuration
```

---

## ⚙️ How It Works

1. **User Authentication**: Users log in with secure credentials
2. **Data Management**: System maintains crypto assets, customer data, transactions, and wallet information
3. **Report Generation**: 
   - Daily reports: Generate transaction summaries for specific dates
   - Monthly reports: Create comprehensive monthly transaction reports
4. **Excel Output**: Reports are generated using OJK-compliant Excel templates
5. **Data Export**: Download reports in Excel format ready for regulatory submission

---

## 📈 Use Case

- For **crypto trading platforms** in Indonesia who need to automate regulatory reporting
- Helps meet **tight deadlines**, reduce **manual input errors**, and ensure **report consistency**
- Suitable for platforms handling multiple cryptocurrencies and customer transactions

---

## 🧪 Installation & Setup

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/ojk-crypto.git
cd ojk-crypto

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Seed the database (optional)
python -m app.scripts.populate_assets

# Create admin user
python -m app.scripts.create_user

# Run the application
python run.py
```

### Docker Deployment

```bash
# Build Docker image
docker build -t ojk-crypto .

# Run container
docker run -p 5000:5000 ojk-crypto
```

Access the application at `http://localhost:5000`

---

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/app.db
```

---

## 📚 References

- [OJK Regulation SEOJK 20/SEOJK.07/2024](https://www.ojk.go.id)
- [POJK 27/2024](https://www.ojk.go.id)
- Brynjolfsson & McAfee, "Financial Automation: The Future of Finance" (2014)
- Kimball & Ross, "ETL Techniques" (2016)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Documentation](https://docs.github.com/en)
- [Python Documentation](https://docs.python.org/3/)

## 👨‍💻 Author

Muhammad Yusuf Ramadhan\
BINUS University - Computer Science\
[LinkedIn](https://www.linkedin.com/in/muhammadyusuframadhan/)
