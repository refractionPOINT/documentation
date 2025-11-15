"""
Shared Chart Utilities for LimaCharlie Reporting
Provides static chart generation for PDF/non-interactive formats
"""

import base64
from io import BytesIO


def generate_static_chart(chart_data, chart_type='line', title='Chart', **kwargs):
    """
    Generate a static chart using matplotlib for PDF/non-interactive formats

    Args:
        chart_data: Dictionary with 'labels' and 'data' keys
        chart_type: 'line', 'bar', or 'pie'
        title: Chart title
        **kwargs: Additional options (width, height, colors, etc.)

    Returns:
        Base64-encoded PNG image string (data:image/png;base64,...)
        Returns None if chart generation fails
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime

        # Get dimensions from kwargs
        width = kwargs.get('width', 10)
        height = kwargs.get('height', 5)
        dpi = kwargs.get('dpi', 100)
        color = kwargs.get('color', '#667eea')

        # Create figure with good DPI for quality
        fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)

        labels = chart_data.get('labels', [])
        data = chart_data.get('data', [])

        if not labels or not data:
            plt.close(fig)
            return None

        # Generate chart based on type
        if chart_type == 'line':
            _generate_line_chart(ax, labels, data, color)
        elif chart_type == 'bar':
            _generate_bar_chart(ax, labels, data, color)
        elif chart_type == 'pie':
            _generate_pie_chart(ax, labels, data)
        else:
            plt.close(fig)
            return None

        # Common styling
        ax.set_title(title, fontsize=14, fontweight='bold', color='#333', pad=15)

        plt.tight_layout()

        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)

        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        print(f"Warning: Could not generate static chart: {e}")
        return None


def _generate_line_chart(ax, labels, data, color):
    """Generate a line chart"""
    from datetime import datetime
    import matplotlib.dates as mdates

    # Convert string dates to datetime if needed
    x_data = labels
    if labels and isinstance(labels[0], str):
        try:
            x_data = [datetime.strptime(label, '%Y-%m-%d') for label in labels]
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(labels)//10)))
        except:
            # If date parsing fails, use labels as-is
            pass

    # Plot line
    ax.plot(x_data, data, marker='o', linewidth=2, markersize=4, color=color)
    ax.fill_between(range(len(data)), data, alpha=0.3, color=color)

    # Styling
    ax.set_ylabel('Count', fontsize=10, color='#666')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.xticks(fontsize=9, color='#666', rotation=45, ha='right')
    plt.yticks(fontsize=9, color='#666')


def _generate_bar_chart(ax, labels, data, color):
    """Generate a bar chart"""
    import matplotlib.pyplot as plt

    # Handle long labels
    if len(labels) > 15:
        labels = [label[:20] + '...' if len(str(label)) > 20 else label for label in labels]

    ax.bar(range(len(labels)), data, color=color, alpha=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)

    # Styling
    ax.set_ylabel('Count', fontsize=10, color='#666')
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.yticks(fontsize=9, color='#666')


def _generate_pie_chart(ax, labels, data):
    """Generate a pie chart"""
    import matplotlib.pyplot as plt

    # Filter out zero values
    filtered = [(l, d) for l, d in zip(labels, data) if d > 0]
    if not filtered:
        return

    labels, data = zip(*filtered)

    # Limit to top 10 items for readability
    if len(labels) > 10:
        sorted_items = sorted(zip(data, labels), reverse=True)
        top_data, top_labels = zip(*sorted_items[:10])
        other_sum = sum(sorted_items[i][0] for i in range(10, len(sorted_items)))
        if other_sum > 0:
            data = list(top_data) + [other_sum]
            labels = list(top_labels) + ['Other']
        else:
            data, labels = top_data, top_labels

    # Color palette
    colors = plt.cm.Set3(range(len(labels)))

    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        data,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 9}
    )

    # Style percentages
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(8)

    ax.axis('equal')


def should_use_static_charts(output_format):
    """
    Determine if static charts should be used based on output format

    Args:
        output_format: 'html', 'pdf', 'markdown'

    Returns:
        Boolean indicating whether to use static charts
    """
    return output_format in ['pdf', 'markdown']


# Export public API
__all__ = ['generate_static_chart', 'should_use_static_charts']
