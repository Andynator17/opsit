"""Check registered routes in the running app"""
import sys
sys.path.insert(0, r"D:\projects\workspace\OpsIT\backend")

from app.main import app

print("All routes containing 'portal':")
for route in app.routes:
    path = getattr(route, 'path', '')
    if 'portal' in path.lower():
        methods = getattr(route, 'methods', set())
        print(f"  {methods} {path}")

print("\nAll routes:")
for route in app.routes:
    path = getattr(route, 'path', '')
    methods = getattr(route, 'methods', set())
    if methods:
        print(f"  {methods} {path}")
