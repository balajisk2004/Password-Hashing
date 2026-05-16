import bcrypt
import mysql.connector
import re
import getpass
from datetime import datetime, timedelta

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root', 
            database='secure_auth'
        )
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Make sure MySQL is running and credentials are correct")
        return None
    
#  PASSWORD HELPER FUNCTIONS
def hash_password(password):
    # Convert plain password into secure hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(plain_password, hashed_password):
    # Verify if password matches the hash
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def is_password_strong(password):
    # Check if password meets minimum requirements
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password needs an uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password needs a lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password needs a number"
    if not re.search(r"[!@#$%^&*]", password):
        return False, "Password needs a special character (!@#$%^&*)"
    return True, "Password is strong"

#  MAIN FEATURES
def register_user(connection, username, email, password, confirm_password):
    # Create a new user account
    
    # Check if passwords match
    if password != confirm_password:
        return False, " Passwords do not match! Please re-enter."
    
    cursor = connection.cursor()
    
    # Check if username or email already exists
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        return False, "Username or email already exists!"
    
    # Check password strength
    is_strong, message = is_password_strong(password)
    if not is_strong:
        cursor.close()
        return False, f" {message}"
    
    # Hash the password
    hashed_pw = hash_password(password)
    
    # Save to database
    try:
        sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, email, hashed_pw))
        connection.commit()
        cursor.close()
        return True, "✅ Registration successful! You can now login."
    except Exception as e:
        cursor.close()
        return False, f" Registration failed: {e}"

def login_user(connection, username_or_email, password):
    # Verify user credentials
    cursor = connection.cursor(dictionary=True)
    
    # Find user in database
    sql = "SELECT * FROM users WHERE username = %s OR email = %s"
    cursor.execute(sql, (username_or_email, username_or_email))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        return False, " User not found"
    
    # Check if account is locked
    if user['lockout_time'] and user['lockout_time'] > datetime.now():
        remaining = (user['lockout_time'] - datetime.now()).seconds // 60
        cursor.close()
        return False, f"Account locked! Try again in {remaining} minutes"
    
    # Verify password
    if check_password(password, user['password_hash']):
        # Successful login - reset failed attempts
        sql = "UPDATE users SET failed_attempts = 0, lockout_time = NULL WHERE id = %s"
        cursor.execute(sql, (user['id'],))
        connection.commit()
        cursor.close()
        return True, f"✅ Welcome back, {user['username']}!"
    else:
        # Failed login - increment counter
        new_attempts = user['failed_attempts'] + 1
        
        if new_attempts >= 5:
            # Lock account
            lock_time = datetime.now() + timedelta(minutes=15)
            sql = "UPDATE users SET failed_attempts = %s, lockout_time = %s WHERE id = %s"
            cursor.execute(sql, (new_attempts, lock_time, user['id']))
            message = " Too many failures! Account locked for 15 minutes"
        else:
            sql = "UPDATE users SET failed_attempts = %s WHERE id = %s"
            cursor.execute(sql, (new_attempts, user['id']))
            message = f" Wrong password! {5 - new_attempts} attempts left"
        
        connection.commit()
        cursor.close()
        return False, message

def change_password(connection, username, old_password, new_password, confirm_password):
    # Change user's password
    
    # Check if new passwords match
    if new_password != confirm_password:
        return False, " New passwords do not match!"
    
    cursor = connection.cursor(dictionary=True)
    
    # Get user
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        return False, " User not found"
    
    # Verify old password
    if not check_password(old_password, user['password_hash']):
        cursor.close()
        return False, " Current password is incorrect"
    
    # Check new password strength
    is_strong, message = is_password_strong(new_password)
    if not is_strong:
        cursor.close()
        return False, f" {message}"
    
    # Update password
    new_hashed = hash_password(new_password)
    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hashed, user['id']))
    connection.commit()
    cursor.close()
    
    return True, " Password changed successfully!"

#  MENU SYSTEM (User Interface)

def show_menu():
    # Display main menu options
    print("\n" + "="*50)
    print("    SIMPLE LOGIN SYSTEM")
    print("="*50)
    print("1. Register New Account")
    print("2. Login")
    print("3. Change Password")
    print("4. Exit")
    print("="*50)

def main():
    # Main program loop
    # Connect to database
    db = connect_to_db()
    if not db:
        return
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-4): ").strip()
        
        # REGISTER
        if choice == '1':
            print("\n" + "="*50)
            print(" REGISTER NEW ACCOUNT")
            print("="*50)
            print("\nPassword requirements:")
            print("  ✓ 8+ characters")
            print("  ✓ One uppercase letter (A-Z)")
            print("  ✓ One lowercase letter (a-z)")
            print("  ✓ One number (0-9)")
            print("  ✓ One special character (!@#$%^&*)")
            print()
            
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            
            print("\n⚠️  Password will not be visible while typing")
            password = getpass.getpass("Password: ")
            confirm_password = getpass.getpass("Confirm Password: ")
            
            # Clear line for better visibility
            print()
            
            success, message = register_user(db, username, email, password, confirm_password)
            print(message)
            
            if success:
                input("\nPress Enter to continue...")
        
        # LOGIN
        elif choice == '2':
            print("\n" + "="*50)
            print("🔑 LOGIN")
            print("="*50)
            
            username = input("Username or Email: ").strip()
            password = getpass.getpass("Password: ")
            
            print()
            success, message = login_user(db, username, password)
            print(message)
            
            if success:
                input("\nPress Enter to continue...")
        
        # CHANGE PASSWORD
        elif choice == '3':
            print("\n" + "="*50)
            print("🔄 CHANGE PASSWORD")
            print("="*50)
            
            username = input("Username: ").strip()
            old_password = getpass.getpass("Current password: ")
            
            print("\nNew password requirements:")
            print("  ✓ 8+ characters")
            print("  ✓ One uppercase letter")
            print("  ✓ One lowercase letter")
            print("  ✓ One number")
            print("  ✓ One special character (!@#$%^&*)")
            print()
            
            new_password = getpass.getpass("New password: ")
            confirm_password = getpass.getpass("Confirm new password: ")
            
            print()
            success, message = change_password(db, username, old_password, new_password, confirm_password)
            print(message)
        
        # EXIT
        elif choice == '4':
            print("\n" + "="*50)
            print("👋 Goodbye! Have a great day!")
            print("="*50)
            db.close()
            break
        
        else:
            print(" Invalid choice! Please enter 1, 2, 3, or 4")




if __name__ == "__main__":
    print("\n" + "="*50)
    print(" Starting Secure Login System...")
    print("="*50)
    main()