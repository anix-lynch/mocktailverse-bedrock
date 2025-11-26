#!/usr/bin/env python3
"""
FastAPI Web Dashboard - AWS Data Browser

🎯 PURPOSE: Simple web interface to browse and inspect AWS DynamoDB data locally
📊 FEATURES: HTML table display, data export options, real-time data viewing
🏗️ ARCHITECTURE: FastAPI → AWS boto3 → DynamoDB → HTML templates
⚡ USAGE: Run locally for development, access at http://localhost:8000
"""

import boto3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from typing import List, Dict, Any

app = FastAPI(title="Mocktailverse Dashboard")

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'mocktailverse-jobs')
table = dynamodb.Table(table_name)

# Templates (simple HTML for now)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mocktailverse Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat-box { background: #4CAF50; color: white; padding: 15px; border-radius: 5px; flex: 1; }
        .stat-box h3 { margin: 0 0 10px 0; }
        .stat-box p { margin: 0; font-size: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #4CAF50; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .refresh-btn { background: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px 0; }
        .refresh-btn:hover { background: #1976D2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍹 Mocktailverse Dashboard</h1>
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Records</h3>
                <p>{total_count}</p>
            </div>
            <div class="stat-box" style="background: #2196F3;">
                <h3>Table Name</h3>
                <p style="font-size: 16px;">{table_name}</p>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Processed At</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

def format_table_rows(items: List[Dict[str, Any]]) -> str:
    """Format DynamoDB items as HTML table rows"""
    rows = []
    for item in items:
        # Handle both boto3 resource format (direct values) and low-level format ({'S': 'value'})
        def get_value(key, default='N/A'):
            val = item.get(key, default)
            if isinstance(val, dict):
                return val.get('S', val.get('N', default))
            return val if val != default else default
        
        job_id = get_value('job_id', 'N/A')
        title = get_value('title', 'N/A')
        company = get_value('company', 'N/A')
        location = get_value('location', 'N/A')
        processed_at = get_value('processed_at', 'N/A')
        
        # Format timestamp
        if processed_at != 'N/A' and len(str(processed_at)) > 19:
            processed_at = str(processed_at)[:19]
        
        rows.append(f"""
            <tr>
                <td>{job_id}</td>
                <td>{title}</td>
                <td>{company}</td>
                <td>{location}</td>
                <td>{processed_at}</td>
            </tr>
        """)
    return ''.join(rows)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard view"""
    try:
        # Scan DynamoDB table
        response = table.scan(Limit=50)
        items = response.get('Items', [])
        total_count = len(items)
        
        # Items are already in the right format from boto3 resource
        rows = format_table_rows(items)
        
        html = HTML_TEMPLATE.format(
            total_count=total_count,
            table_name=table_name,
            rows=rows
        )
        return HTMLResponse(content=html)
        
    except Exception as e:
        error_html = f"""
        <html>
        <body style="font-family: Arial; padding: 20px;">
            <h1>Error</h1>
            <p>{str(e)}</p>
            <p>Make sure AWS credentials are configured and DynamoDB table exists.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)

@app.get("/api/data")
async def get_data():
    """API endpoint to get data as JSON"""
    try:
        response = table.scan(Limit=50)
        return {
            "count": len(response.get('Items', [])),
            "items": response.get('Items', [])
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "table": table_name}

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Mocktailverse Dashboard...")
    print("📊 Open your browser to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

