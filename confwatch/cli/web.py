#!/usr/bin/env python3
"""
Web server command for ConfWatch.
"""

import argparse
import sys
import os

# Add the parent directory to the path so we can import the web module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import run_web_server

def main():
    parser = argparse.ArgumentParser(description='Start ConfWatch web server')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    try:
        run_web_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nWeb server stopped.")
    except Exception as e:
        print(f"Error starting web server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 