"""
Base Report Template
Standard interface for creating custom LimaCharlie reports
"""

from abc import ABC, abstractmethod
from .data_collectors import collect_org_info
from .report_helpers import parse_time_range
from .formatters import render_html_report, render_markdown_report, render_json_report, save_report, add_report_metadata


class BaseReport(ABC):
    """
    Base class for all LimaCharlie reports

    Subclasses should implement:
    - collect_data(): Gather all required data
    - get_template_name(): Return Jinja2 template filename (for HTML)
    - get_report_type(): Return descriptive report type name
    """

    def __init__(self, oid, output_format='html', hours_back=None, time_range_days=None, output_path=None, **kwargs):
        """
        Initialize report

        Args:
            oid: Organization ID
            output_format: Output format ('html', 'markdown', 'json')
            hours_back: Number of hours to look back (optional)
            time_range_days: Number of days to look back (optional)
            output_path: Custom output file path (optional)
            **kwargs: Additional parameters specific to report type
        """
        self.oid = oid
        self.output_format = output_format
        self.hours_back = hours_back
        self.time_range_days = time_range_days
        self.output_path = output_path
        self.params = kwargs
        self.data = {}

    @abstractmethod
    def collect_data(self):
        """
        Collect all data needed for the report

        Returns:
            Dictionary containing all report data
        """
        pass

    @abstractmethod
    def get_template_name(self):
        """
        Get Jinja2 template filename for HTML rendering

        Returns:
            Template filename (e.g., 'security_detections.j2')
        """
        pass

    @abstractmethod
    def get_report_type(self):
        """
        Get descriptive report type name

        Returns:
            Report type string (e.g., 'Security Detections Report')
        """
        pass

    def generate(self):
        """
        Generate the complete report

        Returns:
            Formatted report as string
        """
        # Collect data
        print(f"Generating {self.get_report_type()}...")
        self.data = self.collect_data()

        # Add metadata
        add_report_metadata(self.data, self.get_report_type())

        # Render based on output format
        if self.output_format == 'json':
            return render_json_report(self.data)
        elif self.output_format == 'markdown':
            return render_markdown_report(self.data, title=self.get_report_type())
        else:  # html
            return render_html_report(self.data, self.get_template_name())

    def save(self, output_dir=None):
        """
        Generate and save report to file

        Args:
            output_dir: Directory to save report (default: auto-detected)

        Returns:
            Path to saved report file
        """
        content = self.generate()

        # Determine prefix from report type
        prefix = self.get_report_type().lower().replace(' ', '_')

        filepath = save_report(
            content,
            output_format=self.output_format,
            prefix=prefix,
            output_dir=output_dir
        )

        print(f"\\n✓ Report saved to: {filepath}")
        return filepath

    def _format_timestamp(self, ts, fmt='datetime'):
        """
        Helper method to format timestamps.

        Args:
            ts: Unix timestamp (seconds or milliseconds)
            fmt: Output format ('iso', 'datetime', 'date', 'time')

        Returns:
            Formatted timestamp string
        """
        from .report_helpers import format_timestamp
        return format_timestamp(ts, fmt)


class SimpleReport(BaseReport):
    """
    Simple report builder for custom ad-hoc reports

    Allows building reports without subclassing by providing
    data collection function and template name
    """

    def __init__(self, oid, report_type, data_collector_func,
                 template_name=None, output_format='html', **kwargs):
        """
        Initialize simple report

        Args:
            oid: Organization ID
            report_type: Descriptive report type name
            data_collector_func: Function that collects report data
            template_name: Jinja2 template name (for HTML, optional)
            output_format: Output format ('html', 'markdown', 'json')
            **kwargs: Parameters to pass to data collector function
        """
        super().__init__(oid, output_format, **kwargs)
        self.report_type = report_type
        self.data_collector_func = data_collector_func
        self.template_name = template_name

    def collect_data(self):
        """Call the provided data collector function"""
        return self.data_collector_func(self.oid, **self.params)

    def get_template_name(self):
        """Return the provided template name"""
        if self.template_name is None:
            raise ValueError("Template name required for HTML output")
        return self.template_name

    def get_report_type(self):
        """Return the provided report type"""
        return self.report_type


# Example usage template for creating custom reports
def create_custom_report(oid, output_format='html', **params):
    """
    Template for creating a custom report

    Args:
        oid: Organization ID
        output_format: Output format ('html', 'markdown', 'json')
        **params: Custom parameters for your report

    Returns:
        Formatted report as string
    """
    # Import collectors and helpers
    from .data_collectors import collect_org_info, collect_detections
    from .report_helpers import parse_time_range

    # Collect data
    data = {}

    # 1. Organization info
    data['org_info'] = collect_org_info(oid)

    # 2. Time range
    start_time, end_time = parse_time_range(**params)

    # 3. Custom data collection
    # Add your custom data collection here

    # 4. Render report
    if output_format == 'json':
        return render_json_report(data)
    elif output_format == 'markdown':
        return render_markdown_report(data, title='Custom Report')
    else:
        # For HTML, you'll need a custom template
        return render_html_report(data, 'custom_template.j2')


__all__ = [
    'BaseReport',
    'SimpleReport',
    'create_custom_report'
]
