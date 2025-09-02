# QR Code Generator

A flexible Python script and web interface to generate QR codes from URLs with customizable size and format options.

## 🌐 Web Interface

The easiest way to use the QR generator is through the clean, modern web interface:

### Quick Start (Web Interface)

1. **Start the web server:**
   ```bash
   ./start.sh
   ```
   
2. **Open your browser:**
   Go to [http://localhost:5001](http://localhost:5001)

3. **Generate QR codes:**
   - Enter your URL
   - Choose size (width x height)
   - Select format (PNG or SVG)
   - Choose background option
   - Select download location (browser or server folder)
   - Click "Preview" to see it first, or "Generate & Download" to get the file

### Web Interface Features

- 🎨 **Clean, Modern Design**: Beautiful gradient background with card-based layout
- 📱 **Responsive**: Works perfectly on desktop, tablet, and mobile
- 👀 **Live Preview**: See your QR code before downloading
- ⚡ **Instant Generation**: Fast QR code creation with real-time feedback
- 🎯 **User-Friendly**: Intuitive form with clear labels and helpful placeholders
- 🔧 **Flexible Options**: Custom size, format selection, and background control
- 📁 **Download Options**: Choose to download to browser or save to server folder
- 🗂️ **Native File Picker**: Use your system's file explorer to choose download location
- 📋 **File Management**: View and download all generated QR codes from one place

## Features

- Generate QR codes from any URL
- Customizable size (supports both single numbers and width x height format)
- Multiple output formats: PNG, SVG, EPS, PDF
- Background options (with or without white background)
- Download location options (browser download or server storage)
- Native file picker for choosing download location (modern browsers)
- Smart filename generation based on URL content
- File management system to view and download generated codes
- Interactive mode for easy use
- Command-line interface for automation
- Comprehensive error handling and validation

## Installation

### For Web Interface (Recommended)

1. **Clone or download this project**
2. **Run the startup script:**
   ```bash
   ./start.sh
   ```
   This will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Start the web server

### For Command Line Usage

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Interactive Mode (Recommended for beginners)

Run the script without arguments to enter interactive mode:

```bash
python qr_generator.py
```

The script will prompt you for:
- URL to encode
- Size (e.g., "512", "512x512", or "300x400")
- Format (png, svg, eps, pdf)
- Output folder

### Command Line Mode

Generate a QR code with specific parameters:

```bash
# Basic usage
python qr_generator.py "https://www.example.com"

# With custom size and format
python qr_generator.py "https://www.example.com" -s "300x300" -f "svg"

# With custom output folder
python qr_generator.py "https://www.example.com" -o "./my-qr-codes"
```

### Command Line Options

- `url`: The URL to encode in the QR code
- `-s, --size`: Size in format WIDTHxHEIGHT or single number (default: 512x512)
- `-f, --format`: Output format - png, svg, eps, or pdf (default: png)
- `-o, --output`: Output folder (default: ./qr-codes)
- `-i, --interactive`: Run in interactive mode

## Examples

```bash
# Generate a 512x512 PNG QR code
python qr_generator.py "https://www.instagram.com/lowtide.cafe/"

# Generate a 300x300 SVG QR code
python qr_generator.py "https://www.instagram.com/lowtide.cafe/" -s "300x300" -f "svg"

# Generate a 1000x1000 PDF QR code in custom folder
python qr_generator.py "https://www.instagram.com/lowtide.cafe/" -s "1000" -f "pdf" -o "./instagram-qr"
```

## Size Formats

The size parameter accepts multiple formats:
- Single number: `512` (creates 512x512)
- Width x Height: `512x512`
- Custom dimensions: `300x400`

Size limits: 1 to 1000 pixels

## Output Formats

- **PNG**: Best for web use and general purposes
- **SVG**: Vector format, scalable without quality loss
- **EPS**: PostScript format, good for print
- **PDF**: Portable Document Format

## Download Options

### Web Interface Download Modes

1. **Browser Download (Default):**
   - Select "Download to browser (default)"
   - Click "Generate & Download"
   - File downloads directly to your browser's download folder

2. **File Picker (Modern Browsers):**
   - Select "Save to server folder"
   - Click "Browse" to open your system's file explorer
   - Choose any folder on your computer
   - Click "Generate & Save to Server"
   - File is saved directly to your chosen folder
   - Works with Chrome, Edge, Opera, and other modern browsers

3. **Smart Filenames:**
   - QR codes are automatically named based on the URL
   - Example: `instagram.com/lowtide.cafe` becomes `instagram_com_lowtide_cafe.png`
   - Clean, descriptive names that are easy to identify

## Error Handling

The script includes comprehensive error handling for:
- Invalid URLs
- Network connectivity issues
- Invalid size formats
- Unsupported output formats
- File system permissions
- API service errors

## Notes

- The script uses the free QR Server API (http://api.qrserver.com/)
- Generated files are saved with sanitized filenames based on the URL
- The output folder is created automatically if it doesn't exist
- All URLs are automatically prefixed with `https://` if no protocol is specified
