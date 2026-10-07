import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'certificates.db')}")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "generated_certificates"))
