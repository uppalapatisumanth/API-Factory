import base64

HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<style>
/* ... CSS ... */
</style>
</head>
<body>
<h1>Test Report</h1>
</body>
</html>
"""

try:
    # Updated logic using triple quotes
    b64_template = base64.b64encode(HTML_REPORT_TEMPLATE.encode('utf-8')).decode('utf-8')
    rt_content = f"""import base64
HTML_TEMPLATE = base64.b64decode("{b64_template}").decode("utf-8")
"""
    
    print("--- Generated Content Start ---")
    print(rt_content)
    print("--- Generated Content End ---")
    
    # Try to compile it
    compile(rt_content, "generated_report_template.py", "exec")
    print("SUCCESS: Generated content is valid Python")

except Exception as e:
    print(f"FAILURE: {e}")
