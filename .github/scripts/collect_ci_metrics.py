#!/usr/bin/env python3
"""
Collect CI timing metrics from GitHub Actions workflow runs.
This script fetches timing data for the regression test workflow and stores it in JSON format.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Configuration
REPO_OWNER = os.environ.get('GITHUB_REPOSITORY_OWNER', 'slothy-optimizer')
REPO_NAME = os.environ.get('GITHUB_REPOSITORY', 'slothy-optimizer/slothy').split('/')[-1]
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
WORKFLOW_NAME = 'Regression tests'
METRICS_FILE = '.github/ci-metrics/timings.json'
MAX_RUNS = 50  # Keep last 50 runs

def get_workflow_runs():
    """Fetch recent workflow runs for the regression tests."""
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs'
    params = {
        'branch': 'main',
        'status': 'completed',
        'per_page': MAX_RUNS
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    runs = response.json()['workflow_runs']
    # Filter for the regression tests workflow
    return [run for run in runs if run['name'] == WORKFLOW_NAME]

def get_job_timings(run_id):
    """Fetch job timing details for a specific workflow run."""
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs'

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    jobs = response.json()['jobs']
    job_timings = []

    for job in jobs:
        if job['status'] == 'completed':
            started_at = datetime.fromisoformat(job['started_at'].replace('Z', '+00:00'))
            completed_at = datetime.fromisoformat(job['completed_at'].replace('Z', '+00:00'))
            duration = (completed_at - started_at).total_seconds()

            job_timings.append({
                'name': job['name'],
                'duration': duration,
                'conclusion': job['conclusion']
            })

    return job_timings

def load_existing_metrics():
    """Load existing metrics from file if it exists."""
    metrics_path = Path(METRICS_FILE)
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            return json.load(f)
    return {'runs': []}

def save_metrics(metrics):
    """Save metrics to JSON file."""
    metrics_path = Path(METRICS_FILE)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

def main():
    """Main function to collect and store CI metrics."""
    print("Fetching workflow runs...")
    runs = get_workflow_runs()

    if not runs:
        print("No completed workflow runs found on main branch.")
        return

    print(f"Found {len(runs)} completed workflow runs.")

    # Load existing metrics
    metrics = load_existing_metrics()
    existing_run_ids = {run['run_id'] for run in metrics.get('runs', [])}

    # Collect new runs
    new_runs = []
    for run in runs:
        run_id = run['id']

        # Skip if we already have this run
        if run_id in existing_run_ids:
            continue

        print(f"Collecting data for run {run_id}...")

        try:
            job_timings = get_job_timings(run_id)

            # Calculate total duration
            total_duration = sum(job['duration'] for job in job_timings)

            new_runs.append({
                'run_id': run_id,
                'run_number': run['run_number'],
                'created_at': run['created_at'],
                'commit_sha': run['head_sha'][:7],
                'commit_message': run['head_commit']['message'].split('\n')[0] if run['head_commit'] else '',
                'total_duration': total_duration,
                'jobs': job_timings,
                'conclusion': run['conclusion']
            })
        except Exception as e:
            print(f"Error fetching data for run {run_id}: {e}")
            continue

    # Add new runs to metrics
    metrics['runs'].extend(new_runs)

    # Sort by run number (descending) and keep only the most recent runs
    metrics['runs'] = sorted(metrics['runs'], key=lambda x: x['run_number'], reverse=True)
    metrics['runs'] = metrics['runs'][:MAX_RUNS]

    # Update metadata
    metrics['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    metrics['total_runs'] = len(metrics['runs'])

    # Save to file
    save_metrics(metrics)
    print(f"Metrics saved to {METRICS_FILE}")
    print(f"Total runs tracked: {len(metrics['runs'])}")

if __name__ == '__main__':
    main()
