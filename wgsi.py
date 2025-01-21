from app import create_app

# Create the Flask app
app = create_app()

# Expose the Flask app as "application" for WSGI
application = app
