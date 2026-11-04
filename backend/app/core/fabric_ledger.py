"""
Hyperledger Fabric Audit Ledger & Merkle Chain Simulator
KavachSetu – The Ghost Protocol

Maintains an immutable cryptographically chained block ledger for the 'kavach-channel'
auditing all Ghost-Vault events (document uploads, verifications, ZK proofs, consents, sharing, revocations).
Never records raw documents or sensitive personal identifiable information on-chain.
"""

import hashlib
import json
import secrets
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

# Fabric Channel & Chaincode Configuration
FABRIC_CHANNEL = "kavach-channel"
CHAINCODE_ID = "vault-audit-cc"
ENDORSER_PEER = "peer0.org1.kavachsetu.internal"
MSPID = "KavachOrgMSP"


def _compute_merkle_root(tx_hashes: List[str]) -> str:
    """Computes binary Merkle tree root hash from a list of transaction hashes."""
    if not tx_hashes:
        return hashlib.sha256(b"EMPTY_MERKLE_TREE").hexdigest()
    
    current_level = tx_hashes[:]
    while len(current_level) > 1:
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])
        next_level = []
        for i in range(0, len(current_level), 2):
            combined = current_level[i] + current_level[i + 1]
            next_level.append(hashlib.sha256(combined.encode()).hexdigest())
        current_level = next_level
    return current_level[0]


class FabricLedgerService:
    """
    Manages Hyperledger Fabric channel interactions and immutable state commitment.
    """

    @staticmethod
    def create_tx_id() -> str:
        return f"TX-FABRIC-{secrets.token_hex(8).upper()}"

    @staticmethod
    def record_event(
        db: Session,
        user_id: int,
        action_type: str,
        title: str,
        description: str,
        document_hash: Optional[str] = None,
        institution: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits an audit event transaction to the Fabric ledger state.
        Imports models locally to avoid circular dependencies.
        """
        from backend.app.models.blockchain import BlockchainBlock, BlockchainTransaction
        from backend.app.models.activity import Activity

        tx_id = FabricLedgerService.create_tx_id()
        doc_hash = document_hash or hashlib.sha256(f"{action_type}:{title}:{secrets.token_hex(4)}".encode()).hexdigest()

        # Find latest block or create Genesis block
        latest_block = db.query(BlockchainBlock).order_by(BlockchainBlock.block_number.desc()).first()
        if not latest_block:
            # Initialize Genesis Block #0
            genesis_tx_hash = hashlib.sha256(b"GENESIS_INITIAL_FABRIC_CHANNEL_SETUP").hexdigest()
            genesis_block = BlockchainBlock(
                block_number=0,
                previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
                block_hash=hashlib.sha256(f"GENESIS:{FABRIC_CHANNEL}:{time.time()}".encode()).hexdigest(),
                merkle_root=genesis_tx_hash,
                channel_name=FABRIC_CHANNEL,
                chaincode_id=CHAINCODE_ID,
                tx_count=1,
                endorsing_peer=ENDORSER_PEER,
                timestamp=datetime.utcnow()
            )
            db.add(genesis_block)
            db.commit()
            latest_block = genesis_block

        # Check if block has reached max transactions (e.g. 5 transactions per block for demo block creation)
        tx_count_in_block = db.query(BlockchainTransaction).filter(
            BlockchainTransaction.block_number == latest_block.block_number
        ).count()

        target_block = latest_block
        if tx_count_in_block >= 4 and latest_block.block_number >= 0:
            # Seal new block
            new_block_num = latest_block.block_number + 1
            new_block = BlockchainBlock(
                block_number=new_block_num,
                previous_hash=latest_block.block_hash,
                block_hash="PENDING_SEAL",
                merkle_root="PENDING",
                channel_name=FABRIC_CHANNEL,
                chaincode_id=CHAINCODE_ID,
                tx_count=0,
                endorsing_peer=ENDORSER_PEER,
                timestamp=datetime.utcnow()
            )
            db.add(new_block)
            db.commit()
            target_block = new_block

        # Record Blockchain Transaction
        payload_meta = {
            "title": title,
            "description": description,
            "institution": institution or "KavachSetu Network",
            "msp_id": MSPID,
            "state_commitment": doc_hash[:16]
        }
        tx = BlockchainTransaction(
            tx_id=tx_id,
            block_number=target_block.block_number,
            user_id=user_id,
            action_type=action_type,
            document_hash=doc_hash,
            payload_summary=json.dumps(payload_meta),
            status="CONFIRMED",
            timestamp=datetime.utcnow()
        )
        db.add(tx)

        # Update block merkle root & hash
        db.flush()
        block_txs = db.query(BlockchainTransaction).filter(
            BlockchainTransaction.block_number == target_block.block_number
        ).all()
        tx_hashes = [t.tx_id for t in block_txs]
        target_block.merkle_root = _compute_merkle_root(tx_hashes)
        target_block.tx_count = len(block_txs)
        
        block_header = f"{target_block.block_number}:{target_block.previous_hash}:{target_block.merkle_root}"
        target_block.block_hash = hashlib.sha256(block_header.encode()).hexdigest()
        db.commit()

        # Also mirror to general Activity log
        activity = Activity(
            user_id=user_id,
            action_type=action_type,
            title=title,
            description=description,
            ip_masked="127.0.0.1 (Verified Peer)",
            device_info=f"Fabric Peer: {ENDORSER_PEER}",
            timestamp=datetime.utcnow()
        )
        db.add(activity)
        db.commit()

        return {
            "tx_id": tx_id,
            "block_number": target_block.block_number,
            "block_hash": target_block.block_hash,
            "merkle_root": target_block.merkle_root,
            "channel": FABRIC_CHANNEL,
            "status": "CONFIRMED"
        }

    @staticmethod
    def get_explorer_data(db: Session, limit: int = 10) -> Dict[str, Any]:
        """Returns overview and latest blocks/transactions for the Blockchain Audit Explorer."""
        from backend.app.models.blockchain import BlockchainBlock, BlockchainTransaction

        total_blocks = db.query(BlockchainBlock).count()
        total_txs = db.query(BlockchainTransaction).count()

        blocks = db.query(BlockchainBlock).order_by(BlockchainBlock.block_number.desc()).limit(limit).all()
        transactions = db.query(BlockchainTransaction).order_by(BlockchainTransaction.timestamp.desc()).limit(limit * 2).all()

        formatted_blocks = []
        for b in blocks:
            formatted_blocks.append({
                "block_number": b.block_number,
                "block_hash": b.block_hash,
                "previous_hash": b.previous_hash,
                "merkle_root": b.merkle_root,
                "tx_count": b.tx_count,
                "channel_name": b.channel_name,
                "chaincode_id": b.chaincode_id,
                "endorsing_peer": b.endorsing_peer,
                "timestamp": b.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            })

        formatted_txs = []
        for t in transactions:
            meta = {}
            if t.payload_summary:
                try:
                    meta = json.loads(t.payload_summary)
                except Exception:
                    pass
            formatted_txs.append({
                "tx_id": t.tx_id,
                "block_number": t.block_number,
                "action_type": t.action_type,
                "document_hash": t.document_hash,
                "title": meta.get("title", t.action_type),
                "institution": meta.get("institution", "Network"),
                "status": t.status,
                "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            })

        return {
            "network": {
                "channel": FABRIC_CHANNEL,
                "chaincode": CHAINCODE_ID,
                "endorsing_peer": ENDORSER_PEER,
                "msp_id": MSPID,
                "ledger_status": "ONLINE & SYNCHRONIZED",
                "consensus": "Raft BFT Ordering Service",
                "total_blocks": total_blocks,
                "total_transactions": total_txs
            },
            "recent_blocks": formatted_blocks,
            "recent_transactions": formatted_txs
        }
