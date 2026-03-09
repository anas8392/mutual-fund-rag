import os
import sys

# Patch HuggingFace cache directory for serverless environments (Vercel)
# HuggingFace transformers default to ~/.cache which is read-only on Vercel
# /tmp is the only writable directory on Vercel Serverless
if os.getenv("VERCEL") == "1":
    os.environ["HF_HOME"] = "/tmp"
    os.environ["TRANSFORMERS_CACHE"] = "/tmp"

# Prepend the project root to sys.path so dynamic module imports succeed on Vercel
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

# Vercel Serverless looks for the app object in parsing.
from phase5_backend.main import app 
