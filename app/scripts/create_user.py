from app import db, create_app
from app.models import User

app = create_app()

def create_user(user_name, user_password):
    with app.app_context():
        # Check if the user already exists
        existing_user = User.query.filter_by(username=user_name).first()
        if existing_user:
            print(f"User '{user_name}' already exists.")
            return False
        # Create a new user
        new_user = User(username=user_name)
        new_user.set_password(user_password)
        db.session.add(new_user)
        db.session.commit()
        print(f"User '{user_name}' created successfully.")
        return True

if __name__ == "__main__":
    # Example usage
    username = input("Enter username: ")
    password = input("Enter password: ")
    create_user(username, password)