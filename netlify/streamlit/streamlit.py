import os
import subprocess

def handler(event, context):
    streamlit_script = "Home.py"  # Substitua pelo nome do seu script principal do Streamlit
    result = subprocess.run(["streamlit", "run", streamlit_script], capture_output=True, text=True)
    return {
        'statusCode': 200,
        'body': result.stdout
    }
