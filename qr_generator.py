import requests
import os
from urllib.parse import quote
import argparse
import sys

def sanitize_filename(filename):
    """Remove invalid characters from filenames"""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '_', '-')).rstrip()

def generate_filename_from_url(url):
    """
    Generate a meaningful filename from a URL
    
    Args:
        url (str): The URL to generate a filename from
    
    Returns:
        str: A clean, descriptive filename
    """
    from urllib.parse import urlparse
    import re
    
    try:
        # Parse the URL
        parsed = urlparse(url)
        
        # Get domain name
        domain = parsed.netloc.lower()
        
        # Remove common prefixes
        domain = re.sub(r'^www\.', '', domain)
        domain = re.sub(r'^m\.', '', domain)  # mobile sites
        
        # Get path components
        path = parsed.path.strip('/')
        
        # Create filename components
        filename_parts = []
        
        # Add domain
        if domain:
            # Replace dots with underscores for better readability
            domain_clean = domain.replace('.', '_')
            filename_parts.append(domain_clean)
        
        # Add meaningful path components
        if path:
            # Split path and take meaningful parts
            path_parts = [p for p in path.split('/') if p and len(p) > 1]
            
            # Limit to first 2-3 meaningful path parts to keep filename reasonable
            for part in path_parts[:3]:
                # Clean up the part
                clean_part = re.sub(r'[^a-zA-Z0-9_-]', '_', part)
                clean_part = re.sub(r'_+', '_', clean_part)  # Remove multiple underscores
                clean_part = clean_part.strip('_')
                
                if clean_part and len(clean_part) > 1:
                    filename_parts.append(clean_part)
        
        # If no meaningful parts, use a generic name
        if not filename_parts:
            filename_parts = ['qr_code']
        
        # Join parts and limit length
        filename = '_'.join(filename_parts)
        
        # Limit total length to 50 characters
        if len(filename) > 50:
            filename = filename[:50].rstrip('_')
        
        # Ensure it's not empty
        if not filename:
            filename = 'qr_code'
        
        return filename
        
    except Exception:
        # Fallback to generic name if parsing fails
        return 'qr_code'

def validate_size(size_input):
    """Validate and format size input"""
    try:
        # Handle different input formats
        if 'x' in size_input.lower():
            # Format: "512x512" or "512X512"
            width, height = size_input.lower().split('x')
            width, height = int(width.strip()), int(height.strip())
        else:
            # Single number: "512" -> "512x512"
            size = int(size_input)
            width = height = size
        
        # Validate size limits (API supports 1-1000)
        if not (1 <= width <= 1000) or not (1 <= height <= 1000):
            raise ValueError("Size must be between 1 and 1000 pixels")
        
        return f"{width}x{height}"
    except ValueError as e:
        raise ValueError(f"Invalid size format: {e}")

def validate_format(format_input):
    """Validate format input"""
    valid_formats = ['png', 'svg', 'eps', 'pdf']
    format_lower = format_input.lower()
    
    if format_lower not in valid_formats:
        raise ValueError(f"Format must be one of: {', '.join(valid_formats)}")
    
    return format_lower

def generate_qr_code(url, size="512x512", format_type="png", output_folder="./qr-codes", has_background=True, qr_color="000000"):
    """
    Generate a QR code for the given URL
    
    Args:
        url (str): The URL to encode in the QR code
        size (str): Size in format "WIDTHxHEIGHT" or single number
        format_type (str): Output format (png, svg, eps, pdf)
        output_folder (str): Directory to save the QR code
        has_background (bool): Whether to include white background
        qr_color (str): QR code color in hex format without # (default: 000000 - black)
    
    Returns:
        str: Path to the generated QR code file
    """
    try:
        # Validate inputs
        validated_size = validate_size(size)
        validated_format = validate_format(format_type)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Generate meaningful filename from URL
        base_name = generate_filename_from_url(url)
        filename = f"{base_name}.{validated_format}"
        filepath = os.path.join(output_folder, filename)
        
        # QR code generation parameters
        base_url = "http://api.qrserver.com/v1/create-qr-code/"
        qr_params = {
            'size': validated_size,
            'margin': '10',
            'format': validated_format
        }
        
        # Add background and QR code color parameters
        # Remove # from color if present
        clean_color = qr_color.lstrip('#')
        
        if has_background:
            qr_params['bgcolor'] = 'FFFFFF'
            qr_params['color'] = clean_color
        else:
            qr_params['bgcolor'] = 'transparent'
            qr_params['color'] = clean_color
        
        # URL-encode data and build request URL
        encoded_data = quote(url)
        request_url = f"{base_url}?data={encoded_data}"
        for param, value in qr_params.items():
            request_url += f"&{param}={value}"
        
        print(f"Generating QR code for: {url}")
        print(f"Size: {validated_size}, Format: {validated_format}")
        print(f"Request URL: {request_url}")
        
        # Download QR code
        response = requests.get(request_url, timeout=30)
        response.raise_for_status()
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Successfully created: {filepath}")
        return filepath
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")
    except Exception as e:
        raise Exception(f"Failed to create QR code: {e}")

def interactive_mode():
    """Interactive mode for user input"""
    print("🔗 QR Code Generator")
    print("=" * 50)
    
    try:
        # Get URL input
        url = input("Enter the URL to encode: ").strip()
        if not url:
            print("❌ URL cannot be empty!")
            return
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            print(f"Added https:// protocol: {url}")
        
        # Get size input
        size_input = input("Enter size (e.g., '512', '512x512', or '300x400'): ").strip()
        if not size_input:
            size_input = "512"
        
        # Get format input
        format_input = input("Enter format (png, svg, eps, pdf) [default: png]: ").strip()
        if not format_input:
            format_input = "png"
        
        # Get output folder
        output_folder = input("Enter output folder [default: ./qr-codes]: ").strip()
        if not output_folder:
            output_folder = "./qr-codes"
        
        # Generate QR code
        filepath = generate_qr_code(url, size_input, format_input, output_folder)
        print(f"\n🎉 QR code saved to: {filepath}")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description='Generate QR codes from URLs')
    parser.add_argument('url', nargs='?', help='URL to encode in QR code')
    parser.add_argument('-s', '--size', default='512x512', 
                       help='Size in format WIDTHxHEIGHT or single number (default: 512x512)')
    parser.add_argument('-f', '--format', default='png', 
                       choices=['png', 'svg', 'eps', 'pdf'],
                       help='Output format (default: png)')
    parser.add_argument('-o', '--output', default='./qr-codes',
                       help='Output folder (default: ./qr-codes)')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive or not args.url:
        interactive_mode()
    else:
        try:
            filepath = generate_qr_code(args.url, args.size, args.format, args.output)
            print(f"\n🎉 QR code saved to: {filepath}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
