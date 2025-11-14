#!/usr/bin/env python3
"""
Generate an HTML dashboard with CI timing visualizations.
Creates a hierarchical stacked bar chart showing aggregate and individual job timings.
"""

import json
from pathlib import Path
from datetime import datetime

METRICS_FILE = '.github/ci-metrics/timings.json'
DASHBOARD_FILE = '.github/ci-metrics/dashboard.html'

def load_metrics():
    """Load metrics from JSON file."""
    with open(METRICS_FILE, 'r') as f:
        return json.load(f)

def generate_html(metrics):
    """Generate HTML dashboard with Chart.js visualization."""

    # Prepare data for the chart
    runs = metrics.get('runs', [])
    if not runs:
        chart_data = {'labels': [], 'datasets': []}
    else:
        # Sort runs by run number (ascending for chronological order)
        runs = sorted(runs, key=lambda x: x['run_number'])

        # Extract labels (run numbers with commit info)
        labels = [f"#{run['run_number']}" for run in runs]

        # Get all unique job names across all runs
        all_job_names = set()
        for run in runs:
            for job in run.get('jobs', []):
                all_job_names.add(job['name'])

        # Sort job names for consistent ordering
        job_names = sorted(all_job_names)

        # Generate color palette
        colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ]

        # Create datasets for each job
        datasets = []
        for i, job_name in enumerate(job_names):
            data = []
            for run in runs:
                # Find the job in this run
                job_duration = 0
                for job in run.get('jobs', []):
                    if job['name'] == job_name:
                        job_duration = job['duration']
                        break
                data.append(job_duration)

            datasets.append({
                'label': job_name,
                'data': data,
                'backgroundColor': colors[i % len(colors)],
                'borderColor': colors[i % len(colors)],
                'borderWidth': 1
            })

        chart_data = {
            'labels': labels,
            'datasets': datasets
        }

    # Calculate statistics
    if runs:
        total_durations = [run['total_duration'] for run in runs]
        avg_duration = sum(total_durations) / len(total_durations)
        min_duration = min(total_durations)
        max_duration = max(total_durations)
        latest_duration = runs[-1]['total_duration']

        stats = {
            'total_runs': len(runs),
            'avg_duration': f"{avg_duration:.1f}s",
            'min_duration': f"{min_duration:.1f}s",
            'max_duration': f"{max_duration:.1f}s",
            'latest_duration': f"{latest_duration:.1f}s"
        }
    else:
        stats = {
            'total_runs': 0,
            'avg_duration': 'N/A',
            'min_duration': 'N/A',
            'max_duration': 'N/A',
            'latest_duration': 'N/A'
        }

    last_updated = metrics.get('last_updated', 'Unknown')

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SLOTHY CI Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .stat-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}

        .chart-container {{
            padding: 40px 30px;
            position: relative;
            height: 600px;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}

        .info {{
            margin: 20px 30px;
            padding: 20px;
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            border-radius: 4px;
        }}

        .info h3 {{
            color: #1976D2;
            margin-bottom: 10px;
        }}

        .info p {{
            color: #555;
            line-height: 1.6;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .stats {{
                grid-template-columns: 1fr;
            }}

            .chart-container {{
                height: 400px;
                padding: 20px 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 SLOTHY CI Performance Dashboard</h1>
            <p>Monitor regression test execution times and detect performance changes</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Total Runs</div>
                <div class="stat-value">{stats['total_runs']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Average Duration</div>
                <div class="stat-value">{stats['avg_duration']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Minimum Duration</div>
                <div class="stat-value">{stats['min_duration']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Maximum Duration</div>
                <div class="stat-value">{stats['max_duration']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Latest Duration</div>
                <div class="stat-value">{stats['latest_duration']}</div>
            </div>
        </div>

        <div class="info">
            <h3>📊 About This Dashboard</h3>
            <p>
                This dashboard tracks CI execution times for the SLOTHY regression test suite.
                The stacked bar chart below shows the duration of each test job across recent workflow runs.
                This helps identify performance regressions and monitor CI efficiency over time.
            </p>
        </div>

        <div class="chart-container">
            <canvas id="timingChart"></canvas>
        </div>

        <div class="footer">
            <p>Last updated: {last_updated}</p>
            <p>Generated automatically on every merge to main branch</p>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('timingChart').getContext('2d');
        const chartData = {json.dumps(chart_data)};

        const chart = new Chart(ctx, {{
            type: 'bar',
            data: chartData,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'CI Job Execution Times Over Recent Runs',
                        font: {{
                            size: 18,
                            weight: 'bold'
                        }},
                        padding: {{
                            top: 10,
                            bottom: 20
                        }}
                    }},
                    legend: {{
                        display: true,
                        position: 'bottom',
                        labels: {{
                            padding: 15,
                            font: {{
                                size: 11
                            }}
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                let label = context.dataset.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                if (context.parsed.y !== null) {{
                                    label += context.parsed.y.toFixed(1) + 's';
                                }}
                                return label;
                            }},
                            footer: function(items) {{
                                let total = 0;
                                items.forEach(item => {{
                                    total += item.parsed.y;
                                }});
                                return 'Total: ' + total.toFixed(1) + 's';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        stacked: true,
                        title: {{
                            display: true,
                            text: 'Workflow Run Number',
                            font: {{
                                size: 14,
                                weight: 'bold'
                            }}
                        }},
                        grid: {{
                            display: false
                        }}
                    }},
                    y: {{
                        stacked: true,
                        title: {{
                            display: true,
                            text: 'Duration (seconds)',
                            font: {{
                                size: 14,
                                weight: 'bold'
                            }}
                        }},
                        beginAtZero: true,
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }}
                    }}
                }},
                interaction: {{
                    mode: 'index',
                    intersect: false
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    return html_content

def main():
    """Main function to generate the dashboard."""
    print("Loading metrics...")
    metrics = load_metrics()

    print("Generating dashboard HTML...")
    html_content = generate_html(metrics)

    # Save dashboard
    dashboard_path = Path(DASHBOARD_FILE)
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)

    with open(dashboard_path, 'w') as f:
        f.write(html_content)

    print(f"Dashboard saved to {DASHBOARD_FILE}")
    print(f"Tracked {metrics.get('total_runs', 0)} workflow runs")

if __name__ == '__main__':
    main()
