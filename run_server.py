import uvicorn
from backend.app.db.init_db import init_db

if __name__ == "__main__":
    print("=" * 70)
    print("  KAVACHSETU – THE GHOST PROTOCOL")
    print("  Production Personal Digital Identity & Privacy Wallet (Ghost-Vault)")
    print("  Tagline: Prove, Don't Share.")
    print("=" * 70)
    print("-> Initializing AES-256-GCM vault database & synthetic state...")
    init_db()
    print("-> Demo Citizen: Aarav Mehta (user@kavachsetu.demo / GhostProtocol@2026)")
    print("-> Features Active:")
    print("   * Complete Document Vault (11 categories, OCR pre-scan, AES-256-GCM)")
    print("   * ZK Proof Studio (BN254 curve, Age Range Proof, Income Predicate)")
    print("   * Granular Consent Manager (Approve, Reject, Immediate Revocation)")
    print("   * Secure Sharing & Dynamic QR Generator")
    print("   * Hyperledger Fabric Audit Explorer (kavach-channel Merkle verification)")
    print("   * Encrypted Backup & Password Recovery Engine")
    print("-> Live Interactive Web Wallet: http://127.0.0.1:8000")
    print("-> OpenAPI / Swagger Specs:     http://127.0.0.1:8000/docs")
    print("=" * 70)
    
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)
