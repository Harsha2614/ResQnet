from Navi.models import db, User
from Navi.app import app

with app.app_context():
    # View all users
    users = User.query.all()
    print("Existing users:")
    for u in users:
        print(u.id, u.username, u.role)

    # Example: delete user by username
    username_to_delete = input("Enter user name :") # 👈 change this
    user = User.query.filter_by(username=username_to_delete).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"✅ User '{username_to_delete}' deleted successfully!")
    else:
        print(f"⚠️ User '{username_to_delete}' not found.")
