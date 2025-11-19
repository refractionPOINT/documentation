"""
Standardized CLI Argument Parsing and Report Execution
Eliminates duplicated argument parsing across report templates
"""

import sys
import argparse
from typing import Optional, Dict, Any
from .constants import (
    DEFAULT_TIME_RANGE_HOURS,
    DEFAULT_TIME_RANGE_DAYS,
    DEFAULT_OUTPUT_FORMAT,
    SUPPORTED_FORMATS
)


def parse_common_args(
    description: str,
    default_hours: Optional[int] = None,
    default_days: Optional[int] = None,
    require_oid: bool = True,
    custom_args: Optional[list] = None
) -> argparse.Namespace:
    """
    Parse common CLI arguments for report generation.

    Args:
        description: Help text describing what this report does
        default_hours: Default hours back for time range (overrides default_days if set)
        default_days: Default days back for time range
        require_oid: Whether organization ID is required
        custom_args: List of additional argument configs to add
                     Format: [{'name': '--custom', 'help': 'Help text', 'type': str, 'default': None}]

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Organization ID
    if require_oid:
        parser.add_argument(
            'oid',
            help='LimaCharlie Organization ID'
        )
    else:
        parser.add_argument(
            'oid',
            nargs='?',
            help='LimaCharlie Organization ID (optional)'
        )

    # Time range options
    time_group = parser.add_mutually_exclusive_group()

    if default_hours is not None:
        time_default = default_hours
        time_help = f'Hours back to analyze (default: {default_hours})'
    elif default_days is not None:
        time_default = default_days
        time_help = f'Days back to analyze (default: {default_days})'
    else:
        time_default = DEFAULT_TIME_RANGE_HOURS
        time_help = f'Hours back to analyze (default: {DEFAULT_TIME_RANGE_HOURS})'

    time_group.add_argument(
        '--hours',
        type=int,
        default=time_default if default_hours is not None else None,
        help=time_help
    )

    time_group.add_argument(
        '--days',
        type=int,
        default=time_default if default_days is not None and default_hours is None else None,
        help=f'Days back to analyze (alternative to --hours)'
    )

    # Output format
    parser.add_argument(
        '--format',
        choices=SUPPORTED_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help=f'Output format (default: {DEFAULT_OUTPUT_FORMAT})'
    )

    # Output file path
    parser.add_argument(
        '--output',
        help='Custom output file path (default: auto-generated based on report type)'
    )

    # Verbose mode
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    # Custom arguments
    if custom_args:
        for arg_config in custom_args:
            name = arg_config.pop('name')
            parser.add_argument(name, **arg_config)

    return parser.parse_args()


def execute_report(
    report_class,
    args: argparse.Namespace,
    custom_params: Optional[Dict[str, Any]] = None
) -> None:
    """
    Standard report execution wrapper.

    Args:
        report_class: The report class to instantiate (must inherit from BaseReport)
        args: Parsed CLI arguments from parse_common_args()
        custom_params: Additional parameters to pass to report class __init__
    """
    try:
        # Build initialization parameters
        init_params = {
            'oid': args.oid,
            'output_format': args.format
        }

        # Add time range
        if hasattr(args, 'hours') and args.hours is not None:
            init_params['hours_back'] = args.hours
        elif hasattr(args, 'days') and args.days is not None:
            init_params['time_range_days'] = args.days

        # Add custom output path
        if hasattr(args, 'output') and args.output:
            init_params['output_path'] = args.output

        # Add any custom parameters
        if custom_params:
            init_params.update(custom_params)

        # Instantiate report
        report = report_class(**init_params)

        # Generate and save
        if args.verbose:
            print(f"Generating {report.get_report_type()}...")
            print(f"Organization: {args.oid}")
            if 'hours_back' in init_params:
                print(f"Time range: Last {init_params['hours_back']} hours")
            elif 'time_range_days' in init_params:
                print(f"Time range: Last {init_params['time_range_days']} days")
            print(f"Format: {args.format}")

        output_path = report.save()

        print(f"\n✓ Report generated successfully!")
        print(f"  Location: {output_path}")

        return output_path

    except KeyboardInterrupt:
        print("\n\nReport generation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error generating report: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def get_time_params(args: argparse.Namespace) -> Dict[str, int]:
    """
    Extract time range parameters from parsed args.

    Args:
        args: Parsed arguments namespace

    Returns:
        Dict with either 'hours_back' or 'time_range_days'
    """
    if hasattr(args, 'hours') and args.hours:
        return {'hours_back': args.hours}
    elif hasattr(args, 'days') and args.days:
        return {'time_range_days': args.days}
    else:
        return {'hours_back': DEFAULT_TIME_RANGE_HOURS}


# Convenience function for simple reports
def simple_cli(report_class, description: str, **kwargs):
    """
    One-liner CLI setup and execution for simple reports.

    Usage:
        if __name__ == '__main__':
            simple_cli(MyReport, "Generate security detections report")

    Args:
        report_class: Report class to execute
        description: CLI description text
        **kwargs: Additional args passed to parse_common_args()
    """
    args = parse_common_args(description, **kwargs)
    execute_report(report_class, args)
