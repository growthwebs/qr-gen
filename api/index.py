from app import app

# This is the entry point for Vercel
# Vercel will automatically detect this as a Python function
def handler(request):
    return app(request.environ, request.start_response)

# Alternative entry point for Vercel
if __name__ == "__main__":
    app.run()
