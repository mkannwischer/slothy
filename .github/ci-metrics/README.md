# CI Performance Metrics Dashboard

This directory contains the CI performance tracking system for SLOTHY, which monitors regression test execution times and helps detect performance regressions.

## 📊 View the Dashboard

**[Click here to view the CI Performance Dashboard](dashboard.html)**

The dashboard displays:
- Total aggregate CI duration over time
- Individual job execution times in a stacked bar chart
- Statistical summaries (average, min, max durations)
- Historical trends across recent workflow runs

## How It Works

### Automatic Updates

The CI metrics system automatically:

1. **Collects Data**: When commits are merged to the `main` branch, a GitHub Actions workflow runs to collect timing data from recent CI runs
2. **Stores Metrics**: Timing data is stored in `timings.json` with details about each job's execution time
3. **Generates Dashboard**: An HTML dashboard is generated with interactive visualizations
4. **Commits Updates**: The updated metrics and dashboard are committed back to the repository

### Manual Trigger

You can also manually trigger the metrics collection by:

1. Going to the "Actions" tab in GitHub
2. Selecting the "CI Performance Metrics" workflow
3. Clicking "Run workflow"

## Files

- **`dashboard.html`**: Interactive HTML dashboard with visualizations (open in browser)
- **`timings.json`**: Raw timing data in JSON format
- **`README.md`**: This file

## Configuration

The metrics system is configured in:
- **Workflow**: `.github/workflows/ci_metrics.yaml`
- **Collection Script**: `.github/scripts/collect_ci_metrics.py`
- **Dashboard Generator**: `.github/scripts/generate_dashboard.py`

### Customization Options

You can customize the behavior by modifying the scripts:

- **`MAX_RUNS`**: Number of recent runs to track (default: 50)
- **Chart colors**: Edit the color palette in `generate_dashboard.py`
- **Statistics**: Add custom metrics in the dashboard generator

## Data Format

The `timings.json` file contains:

```json
{
  "runs": [
    {
      "run_id": 12345,
      "run_number": 42,
      "created_at": "2024-01-01T12:00:00Z",
      "commit_sha": "abc1234",
      "commit_message": "Fix performance issue",
      "total_duration": 245.3,
      "jobs": [
        {
          "name": "examples_dry_run (target1)",
          "duration": 45.2,
          "conclusion": "success"
        }
      ],
      "conclusion": "success"
    }
  ],
  "last_updated": "2024-01-01T12:30:00Z",
  "total_runs": 42
}
```

## Troubleshooting

### Dashboard not updating

- Check the "CI Performance Metrics" workflow in the Actions tab
- Ensure the workflow has necessary permissions (contents: write, actions: read)
- Verify the GitHub token has access to the Actions API

### Missing data

- The system only tracks completed workflow runs on the `main` branch
- Initial setup requires at least one completed CI run to display data

## Related

This feature addresses [Issue #64](https://github.com/slothy-optimizer/slothy/issues/64) - Log CI time to detect performance regressions.
