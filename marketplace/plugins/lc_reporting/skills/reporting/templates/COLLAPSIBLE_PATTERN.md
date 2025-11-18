# Collapsible Tables Pattern

## Overview

For better UX in HTML reports, tables with more than 10 rows should automatically become collapsible. This prevents overwhelming the user with long lists and improves page performance.

## Pattern

### Automatic Threshold-Based Collapsing

Tables automatically become collapsible when they exceed a threshold (default: 10 rows):

```jinja2
{% if items|length > 10 %}
<details>
    <summary>
        Detection List
        <span class="expand-hint">(Click to expand/collapse)</span>
    </summary>
    <div class="collapsible-content">
        <table>
            <!-- table content -->
        </table>
    </div>
</details>
{% else %}
<table>
    <!-- table content -->
</table>
{% endif %}
```

### Key Features

1. **Threshold-based**: Only applies to lists with >10 items
2. **Default collapsed**: Starts collapsed to keep reports clean and scannable
3. **Visual feedback**: Summary bar changes color when expanded
4. **Print-friendly**: Collapses/expands work with standard HTML `<details>` element
5. **No JavaScript**: Uses native HTML5 `<details>` element

## CSS Styles

Add this to your template's `<style>` section:

```css
/* Collapsible sections */
details {
    margin: 15px 0;
}

details summary {
    cursor: pointer;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    font-weight: 600;
    color: #333;
    user-select: none;
    transition: background 0.2s;
}

details summary:hover {
    background: #e9ecef;
}

details[open] summary {
    background: #667eea;
    color: white;
    border-radius: 8px 8px 0 0;
}

details summary::marker {
    color: #667eea;
}

details[open] summary::marker {
    color: white;
}

details .collapsible-content {
    padding: 0;
    margin-top: 0;
    border: 1px solid #e0e0e0;
    border-top: none;
    border-radius: 0 0 8px 8px;
}

details .collapsible-content table {
    margin: 0;
}

.expand-hint {
    font-size: 0.85em;
    color: #667eea;
    font-weight: normal;
    margin-left: 10px;
}

details[open] .expand-hint {
    color: white;
}
```

## Using Macros (Recommended)

For consistency, use the reusable macros from `macros.j2`:

```jinja2
{% from 'macros.j2' import collapsible_table %}

{% call collapsible_table(
    title="Detection List",
    headers=["Timestamp", "Category", "Rule", "Sensor", "Summary"],
    rows=detections.list,
    threshold=10,
    default_open=False
) %}
    {% for det in rows %}
    <tr>
        <td>{{ det.timestamp }}</td>
        <td>{{ det.category }}</td>
        <td>{{ det.rule }}</td>
        <td>{{ det.sensor_id }}</td>
        <td>{{ det.summary }}</td>
    </tr>
    {% endfor %}
{% endcall %}
```

Or use the simpler `collapsible_section` for any content:

```jinja2
{% from 'macros.j2' import collapsible_section %}

{% call collapsible_section(
    title="Advanced Options",
    item_count=50,
    threshold=20
) %}
    <div>Your content here...</div>
{% endcall %}
```

## Reports Using This Pattern

- ✅ **Incident Investigation**: Detection details table (>10 detections)
- ✅ **Security Detections**: High severity detections table (>10 detections)
- ⏳ **Config Audit**: Configuration items (>10 items) - TODO
- ⏳ **Sensor Status**: Sensor list (>10 sensors) - TODO
- ⏳ **Rule Coverage**: Rules list (>10 rules) - TODO

## Benefits

1. **Improved Performance**: Large tables don't slow down initial page render
2. **Better UX**: Users aren't overwhelmed by long lists
3. **Scannable**: Easy to see section headers and decide what to expand
4. **Accessible**: Native HTML elements work with screen readers
5. **Print-friendly**: Can be styled for printing

## When to Use

Apply this pattern when:

- Table has >10 rows
- List contains >10 items
- Section contains verbose content that can be optionally hidden
- User needs overview first, details second

## When NOT to Use

Avoid this pattern when:

- List has ≤10 items (keep it simple)
- All data must be immediately visible (e.g., critical alerts)
- Table is the primary content of the page
- Data needs to be easily searchable (Ctrl+F won't work on collapsed content in all browsers)

## Customization

You can customize the threshold per-section:

```jinja2
{# Use 20 for longer lists #}
{% if items|length > 20 %}
<details open>
    ...
</details>
{% endif %}

{# Use 5 for very detailed items #}
{% if items|length > 5 %}
<details open>
    ...
</details>
{% endif %}
```

## Future Enhancements

Possible improvements:

1. **Remember state**: Use localStorage to remember collapsed/expanded state
2. **Expand all / Collapse all**: Buttons to control all sections at once
3. **Lazy loading**: Only render table rows when expanded
4. **Search within**: Add search box to filter collapsed content
5. **Progressive disclosure**: Show first N items, collapse rest

## Implementation Checklist

When adding collapsible tables to a new report:

- [ ] Add collapsible CSS styles to `<style>` section
- [ ] Identify tables/lists with >10 items
- [ ] Wrap content in `<details>` with threshold check
- [ ] Add helpful summary text with expand hint
- [ ] Test with various item counts (0, 5, 10, 11, 100+)
- [ ] Verify print styles work correctly
- [ ] Test accessibility with screen readers
