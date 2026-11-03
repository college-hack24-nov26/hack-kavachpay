import uvicorn
from backend.app.db.init_db import init_db

if __name__ == "__main__":
    print("=" * 65)
    print("  KAVACHSETU – THE GHOST PROTOCOL")
    print("  Stage 1: Digital Trust & Financial Verification Engine")
    print("  Tagline: Prove, Don't Share.")
    print("=" * 65)
    print("-> Initializing secure database and synthetic credentials...")
    init_db()
    print("-> Demo user seeded: Aarav Mehta (user@kavachsetu.demo / GhostProtocol@2026)")
    print("-> Credentials seeded: Identity (KVS-ID-001), KYC (KVS-KYC-001), Income (KVS-INC-001)")
    print("-> Web client available at: http://127.0.0.1:8000")
    print("-> Interactive API docs at:  http://127.0.0.1:8000/docs")
    print("=" * 65)
    
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)

