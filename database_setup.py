import os
from app import create_app, db
from app.models import User

# For cloud deployment (Render, Railway, or Heroku)
# DATABASE_URL will be automatically provided by cloud platform

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created!")
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@sports.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@sports.com'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")

if __name__ == '__main__':
    init_db()