from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import tempfile
import time
from qr_generator import generate_qr_code
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Create uploads directory (use /tmp for Vercel serverless)
UPLOAD_FOLDER = '/tmp/qr_codes' if os.environ.get('VERCEL') else 'static/qr_codes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get form data
        url = request.form.get('url', '').strip()
        size = request.form.get('size', '512x512').strip()
        format_type = request.form.get('format', 'png').strip()
        has_background = request.form.get('background') == 'on'
        qr_color = request.form.get('qr_color', '#000000').strip().lstrip('#')
        download_location = request.form.get('download_location', 'browser')
        server_path = request.form.get('server_path', './downloads').strip()
        
        # Validate URL
        if not url:
            flash('Please enter a URL', 'error')
            return redirect(url_for('index'))
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Determine output folder based on download location
        if download_location == 'server' and server_path and not server_path.startswith('selected'):
            # For Vercel, we can't create custom directories, so use temp folder
            if os.environ.get('VERCEL'):
                output_folder = '/tmp'
            else:
                output_folder = os.path.abspath(server_path)
                os.makedirs(output_folder, exist_ok=True)
        else:
            # Use default upload folder for browser download or file picker
            output_folder = UPLOAD_FOLDER
        
        # Generate QR code with meaningful filename
        generated_file = generate_qr_code(
            url=url,
            size=size,
            format_type=format_type,
            output_folder=output_folder,
            has_background=has_background,
            qr_color=qr_color
        )
        
        # The generate_qr_code function now returns a file with a meaningful name
        filepath = generated_file
        
        if download_location == 'server' and server_path and not server_path.startswith('selected'):
            # Return success message with file path (manual server storage)
            flash(f'QR code saved successfully to: {filepath}', 'success')
            return redirect(url_for('index'))
        else:
            # Return the generated QR code for download (browser download or file picker)
            filename = os.path.basename(filepath)
            return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Error generating QR code: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/preview', methods=['POST'])
def preview():
    try:
        # Get form data
        url = request.form.get('url', '').strip()
        size = request.form.get('size', '512x512').strip()
        format_type = request.form.get('format', 'png').strip()
        has_background = request.form.get('background') == 'on'
        qr_color = request.form.get('qr_color', '#000000').strip().lstrip('#')
        
        # Validate URL
        if not url:
            flash('Please enter a URL', 'error')
            return redirect(url_for('index'))
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Generate preview QR code with meaningful name
        generated_file = generate_qr_code(
            url=url,
            size=size,
            format_type=format_type,
            output_folder=UPLOAD_FOLDER,
            has_background=has_background,
            qr_color=qr_color
        )
        
        # For preview, we'll use the generated file directly
        temp_filepath = generated_file
        
        # Get just the filename from the full path
        temp_filename = os.path.basename(temp_filepath)
        
        # Return preview data with cache-busting timestamp
        timestamp = int(time.time() * 1000)  # milliseconds
        
        # For Vercel, we need to serve from the correct path
        if os.environ.get('VERCEL'):
            preview_url = f'/tmp/qr_codes/{temp_filename}?t={timestamp}'
        else:
            preview_url = f'/static/qr_codes/{temp_filename}?t={timestamp}'
            
        return {
            'success': True,
            'preview_url': preview_url,
            'filename': temp_filename
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/files')
def list_files():
    """List all generated QR code files"""
    try:
        files = []
        # For Vercel, we can't list files from /tmp, so return empty list
        if os.environ.get('VERCEL'):
            files = []
        else:
            for folder in ['static/qr_codes', 'downloads']:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        # Look for QR code files (any file with supported extensions)
                        if filename.endswith(('.png', '.svg', '.eps', '.pdf')):
                            filepath = os.path.join(folder, filename)
                            file_size = os.path.getsize(filepath)
                            files.append({
                                'name': filename,
                                'path': filepath,
                                'size': file_size,
                                'folder': folder
                            })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(x['path']), reverse=True)
        
        return render_template('files.html', files=files)
    except Exception as e:
        flash(f'Error listing files: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download a specific file"""
    try:
        # Security check - only allow files in allowed directories
        if os.environ.get('VERCEL'):
            # For Vercel, files are in /tmp
            filepath = os.path.join('/tmp', filename)
            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True)
        else:
            allowed_dirs = ['static/qr_codes', 'downloads']
            for allowed_dir in allowed_dirs:
                filepath = os.path.join(allowed_dir, filename)
                if os.path.exists(filepath) and os.path.commonpath([os.path.abspath(filepath), os.path.abspath(allowed_dir)]) == os.path.abspath(allowed_dir):
                    return send_file(filepath, as_attachment=True)
        
        flash('File not found or access denied', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/tmp/qr_codes/<filename>')
def serve_temp_qr(filename):
    """Serve temporary QR code files for preview on Vercel"""
    try:
        filepath = os.path.join('/tmp/qr_codes', filename)
        if os.path.exists(filepath):
            return send_file(filepath)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error serving file: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
