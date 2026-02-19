#!/usr/bin/env python3
"""
Command-line interface for cmake_generator
"""

import argparse
import sys
from pathlib import Path
from .generator import CMakeGenerator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate CMakeLists.txt from YAML configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  cmake-gen config.yaml
  cmake-gen config.yaml -o build/CMakeLists.txt
  cmake-gen --help
        """
    )
    
    parser.add_argument(
        'config',
        type=str,
        help='Path to YAML configuration file'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='CMakeLists.txt',
        help='Output path for CMakeLists.txt (default: CMakeLists.txt)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file '{args.config}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Generate CMakeLists.txt
        generator = CMakeGenerator.from_yaml(args.config)
        generator.write_to_file(args.output)
        print(f"Successfully generated {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
