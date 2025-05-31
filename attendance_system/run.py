import argparse
from app import create_app, create_db, db # Corrected import

# Create the app instance using the factory
app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Manage the Flask application.")
    parser.add_argument('action', nargs='?', help="Action to perform (e.g., 'create_db')")
    args = parser.parse_args()

    if args.action == 'create_db':
        print("Creating database...")
        with app.app_context(): # Ensure app context is active for db operations
            create_db(app)
        print("Database created successfully.")
    else:
        print("Starting Flask development server...")
        app.run(debug=True)
