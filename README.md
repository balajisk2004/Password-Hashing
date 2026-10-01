# 🔐 Secure Authentication System

A command-line authentication system built with Python and MySQL that implements strong security practices for user registration, login, and password management.

## ✨ Features

### Core Features
- ✅ **User Registration** — Create new accounts with email validation
- ✅ **Secure Login** — Authenticate using username or email
- ✅ **Password Change** — Update password with current password verification

### Security Features
- 🔐 **bcrypt Password Hashing** — Industry-standard hashing with automatic salt
- 🚫 **Account Lockout** — Automatic 15-minute lock after 5 failed attempts
- 🛡️ **SQL Injection Prevention** — Parameterized queries throughout
- ✔️ **Password Strength Validation** — Enforces 5 security criteria
- 🔒 **No Plain-Text Storage** — Passwords are never stored in readable form
- 📝 **Input Validation** — User inputs are validated before processing
- ⚠️ **Error Handling** — Graceful handling of common edge cases

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.x | Core programming language |
| MySQL 8.0 | Relational database management |
| bcrypt | Password hashing library |
| mysql-connector-python | MySQL database connectivity |
| getpass | Secure password input |
| datetime | Account lockout timing |
| re | Password validation regex |

---

## 🔒 Security Implementation

### 1. Password Hashing (bcrypt)

```python
def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
```

- Uses **12 rounds** — computationally expensive for attackers
- **Unique salt per user** — prevents rainbow table attacks
- **One-way hashing** — passwords cannot be reversed

### 2. Password Strength Validation

Passwords must contain:

- ✅ Minimum 8 characters
- ✅ At least one uppercase letter (A-Z)
- ✅ At least one lowercase letter (a-z)
- ✅ At least one digit (0-9)
- ✅ At least one special character (`!@#$%^&*`)

### 3. Account Lockout Protection

| Failed Attempts | Action |
|-----------------|--------|
| 1-4 | Warning with remaining attempts |
| 5 | Account locked for 15 minutes |
| After lockout | Automatic unlock after duration |

### 4. SQL Injection Prevention

```python
# ✅ SAFE - Parameterized query
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

# ❌ NEVER DO THIS
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip package manager

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/secure-auth-system.git
cd secure-auth-system
```

### Step 2: Install Dependencies

```bash
pip install bcrypt mysql-connector-python
```

Or install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Database

Open `login_system.py` and update the database credentials:

```python
def connect_to_db():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='your_password',  # ⚠️ Change this!
        database='secure_auth'
    )
```

> **Tip:** Don't commit real credentials to GitHub. Consider reading them from environment variables instead.

---

## 💾 Database Setup

Run these SQL commands in MySQL (or run `database_setup.sql`):

```sql
-- Create database
CREATE DATABASE secure_auth;
USE secure_auth;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    failed_attempts INT DEFAULT 0,
    lockout_time DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verify table creation
DESCRIBE users;
```

---

## 🎮 Usage

### Run the Program

```bash
python login_system.py
```

### Main Menu

```text
==================================================
   🔐 SIMPLE LOGIN SYSTEM
==================================================
1. Register New Account
2. Login
3. Change Password
4. Exit
==================================================
```

### Example Workflow

**1️⃣ Register a New Account**

```text
Username: john_doe
Email: john@example.com
Password: MyPass@123
Confirm Password: MyPass@123

✅ Registration successful! You can now login.
```

**2️⃣ Login**

```text
Username or Email: john_doe
Password: MyPass@123

✅ Welcome back, john_doe!
```

**3️⃣ Failed Login (Account Lockout)**

```text
Username: john_doe
Password: wrongpass

❌ Wrong password! 4 attempts left
❌ Wrong password! 3 attempts left
❌ Wrong password! 2 attempts left
❌ Wrong password! 1 attempt left
❌ Too many failures! Account locked for 15 minutes
```

**4️⃣ Change Password**

```text
Username: john_doe
Current password: MyPass@123
New password: NewPass@456
Confirm new password: NewPass@456

✅ Password changed successfully!
```

---

## 📁 Project Structure

```text
secure-auth-system/
│
├── login_system.py         # Main application
├── requirements.txt        # Dependencies
├── README.md               # Documentation
├── database_setup.sql      # Database schema
└── screenshots/            # Demo images
    ├── register.png
    ├── login.png
    └── locked.png
```

---

## 🔄 How It Works

### Registration Flow

```text
User Input → Validate Password Strength → Check Duplicate → Hash Password → Save to DB → Success
```

### Login Flow

```text
User Input → Find User → Check Lockout → Verify Password →
    ├── ✅ Correct → Reset Attempts → Login Success
    └── ❌ Wrong → Increment Attempts → Lock if ≥ 5
```

### Password Change Flow

```text
User Input → Verify Old Password → Validate New Password → Hash → Update DB → Success
```

---

## 🧪 Testing

### Test Cases Covered

| Test Case | Expected Result |
|-----------|-----------------|
| Register with strong password | ✅ Success |
| Register with weak password | ❌ Rejected with reason |
| Register with existing username | ❌ Duplicate error |
| Login with correct credentials | ✅ Success |
| Login with wrong password | ❌ Attempts counter decreases |
| 5 failed login attempts | 🔒 Account locked 15 min |
| Password mismatch in registration | ❌ "Passwords don't match" |
| SQL injection attempt | 🛡️ Blocked by parameterized query |

### Manual Testing

```text
# Test 1: Register
Username: testuser
Email: test@example.com
Password: Test@1234
Confirm: Test@1234

# Test 2: Login (correct)
Username: testuser
Password: Test@1234

# Test 3: Login (wrong - 5 times to trigger lockout)
Password: wrongpass
```

---

## 📸 Screenshots

### Registration Screen

```text
==================================================
📝 REGISTER NEW ACCOUNT
==================================================

Password requirements:
  ✓ 8+ characters
  ✓ One uppercase letter (A-Z)
  ✓ One lowercase letter (a-z)
  ✓ One number (0-9)
  ✓ One special character (!@#$%^&*)

Username: john_doe
Email: john@example.com
Password: ********
Confirm Password: ********

✅ Registration successful! You can now login.
```

### Login Screen

```text
==================================================
🔑 LOGIN
==================================================

Username or Email: john_doe
Password: ********

✅ Welcome back, john_doe!
```

### Account Locked Screen

```text
==================================================
🔑 LOGIN
==================================================

Username or Email: john_doe
Password: ********

❌ Too many failures! Account locked for 15 minutes
```


## ⭐ Show Your Support

If this project helped you, please give it a ⭐ on GitHub!
