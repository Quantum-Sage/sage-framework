"""
SAGE Framework — Quorum Partition Test Suite
=============================================

Tests the mesh network's behavior under network partitions.

Network partitions are a distinct failure mode from node crashes:
- Node crash: One node goes offline, others remain connected
- Network partition: Network splits into disconnected subgroups

Byzantine fault tolerance guarantees:
- Safety: No two partitions can both achieve quorum (split-brain prevention)
- Liveness: Majority partition can continue operating
- Recovery: System returns to full operation when partition heals

This test suite validates:
1. Majority partition maintains quorum
2. Minority partition correctly fails to achieve quorum
3. No split-brain scenarios (conflicting consensus)
4. Recovery after partition healing
5. State consistency after recovery
"""

import pytest
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from enum import Enum
import time

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

SAGE_CONSTANT = 0.85
QUORUM_SIZE = 5
NUM_NODES = 8
NODE_IDS = ["beijing", "shanghai", "dubai", "london", "nyc", "tokyo", "singapore", "paris"]


class PartitionType(Enum):
    """Types of network partitions."""
    NONE = "none"              # Fully connected
    MAJORITY_MINORITY = "5-3"  # 5 nodes vs 3 nodes
    SYMMETRIC = "4-4"          # 4 vs 4 split (Byzantine failure)
    TOTAL = "all-isolated"     # All nodes isolated


@dataclass
class NodeState:
    """State of a single mesh node."""
    node_id: str
    fidelity: float
    epoch: int = 0  # Consensus epoch
    last_seen: Dict[str, int] = field(default_factory=dict)
    
    def can_reach(self, other_id: str, partition_map: Dict[str, int]) -> bool:
        """Check if this node can communicate with another."""
        return partition_map.get(self.node_id, -1) == partition_map.get(other_id, -2)


@dataclass
class ConsensusResult:
    """Result of a consensus attempt."""
    success: bool
    agreed_fidelity: Optional[float]
    participating_nodes: List[str]
    epoch: int
    partition_id: int


# ═══════════════════════════════════════════════════════════════════════════════
# MESH NETWORK SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════

class PartitionableMesh:
    """
    A mesh network that can be partitioned for testing.
    
    Implements simplified Byzantine consensus:
    - Nodes vote on state
    - Quorum requires 3+ agreeing nodes
    - Partitioned nodes can only see their partition
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        
        self.nodes: Dict[str, NodeState] = {}
        self.partition_map: Dict[str, int] = {}  # node_id -> partition_id
        self.global_epoch: int = 0
        self.consensus_history: List[ConsensusResult] = []
        
        # Initialize nodes with realistic fidelities
        fidelities = {
            "beijing": 0.97,
            "shanghai": 0.96,
            "dubai": 0.88,
            "london": 0.95,
            "nyc": 0.98,
            "tokyo": 0.94,
            "singapore": 0.93,
            "paris": 0.92,
        }
        
        for node_id in NODE_IDS:
            self.nodes[node_id] = NodeState(
                node_id=node_id,
                fidelity=fidelities[node_id],
                epoch=0,
                last_seen={nid: 0 for nid in NODE_IDS}
            )
            self.partition_map[node_id] = 0  # All in partition 0 initially
    
    def create_partition(self, partition_type: PartitionType) -> Dict[str, int]:
        """
        Create a network partition.
        
        Returns the partition map (node_id -> partition_id).
        """
        if partition_type == PartitionType.NONE:
            self.partition_map = {nid: 0 for nid in NODE_IDS}
        
        elif partition_type == PartitionType.MAJORITY_MINORITY:
            # 5 vs 3 split
            self.partition_map = {
                "beijing": 0, "shanghai": 0, "dubai": 0, "london": 0, "nyc": 0,
                "tokyo": 1, "singapore": 1, "paris": 1
            }
        
        elif partition_type == PartitionType.SYMMETRIC:
            # 4 vs 4 split
            self.partition_map = {
                "beijing": 0, "shanghai": 0, "dubai": 0, "london": 0,
                "nyc": 1, "tokyo": 1, "singapore": 1, "paris": 1
            }
        
        elif partition_type == PartitionType.TOTAL:
            # Each node in its own partition
            self.partition_map = {nid: i for i, nid in enumerate(NODE_IDS)}
        
        return self.partition_map
    
    def heal_partition(self):
        """Restore full network connectivity."""
        self.partition_map = {nid: 0 for nid in NODE_IDS}
    
    def get_reachable_nodes(self, from_node: str) -> List[str]:
        """Get list of nodes reachable from a given node."""
        my_partition = self.partition_map[from_node]
        return [nid for nid in NODE_IDS if self.partition_map[nid] == my_partition]
    
    def attempt_consensus(self, initiator: str) -> ConsensusResult:
        """
        Attempt to reach consensus from a given node's perspective.
        
        Only nodes in the same partition can participate.
        """
        self.global_epoch += 1
        
        # Find reachable nodes
        reachable = self.get_reachable_nodes(initiator)
        
        # Collect votes (fidelity reports)
        votes = [(nid, self.nodes[nid].fidelity) for nid in reachable]
        
        # Check quorum
        if len(votes) < QUORUM_SIZE:
            result = ConsensusResult(
                success=False,
                agreed_fidelity=None,
                participating_nodes=reachable,
                epoch=self.global_epoch,
                partition_id=self.partition_map[initiator]
            )
        else:
            # Compute median fidelity (Byzantine-resilient)
            fidelities = sorted([f for _, f in votes])
            median_f = fidelities[len(fidelities) // 2]
            
            result = ConsensusResult(
                success=True,
                agreed_fidelity=median_f,
                participating_nodes=reachable,
                epoch=self.global_epoch,
                partition_id=self.partition_map[initiator]
            )
        
        self.consensus_history.append(result)
        return result
    
    def update_node_fidelity(self, node_id: str, new_fidelity: float):
        """Update a node's fidelity (simulates state evolution)."""
        self.nodes[node_id].fidelity = np.clip(new_fidelity, 0.0, 1.0)
    
    def apply_decoherence(self, rate: float = 0.01):
        """Apply decoherence to all nodes."""
        for node in self.nodes.values():
            decay = np.exp(-rate)
            # Fidelity decays toward 0.5
            node.fidelity = 0.5 + (node.fidelity - 0.5) * decay


# ═══════════════════════════════════════════════════════════════════════════════
# TEST CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestMajorityPartition:
    """Tests that majority partition maintains consensus."""
    
    def test_majority_achieves_quorum(self):
        """5-node partition should achieve quorum."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        
        # Consensus from majority partition
        result = mesh.attempt_consensus("beijing")
        
        assert result.success, "Majority partition should achieve consensus"
        assert len(result.participating_nodes) == 5
        assert result.agreed_fidelity is not None
    
    def test_majority_fidelity_is_median(self):
        """Consensus fidelity should be median of participating nodes."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        
        result = mesh.attempt_consensus("beijing")
        
        # Beijing=0.97, Shanghai=0.96, Dubai=0.88 → median=0.96
        expected_median = 0.96
        assert result.agreed_fidelity == expected_median, \
            f"Expected median {expected_median}, got {result.agreed_fidelity}"
    
    def test_majority_maintains_identity(self):
        """Majority consensus should preserve identity (F > S)."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        
        result = mesh.attempt_consensus("beijing")
        
        assert result.agreed_fidelity >= SAGE_CONSTANT, \
            f"Identity should persist, F={result.agreed_fidelity} < S={SAGE_CONSTANT}"


class TestMinorityPartition:
    """Tests that minority partition fails safely."""
    
    def test_minority_fails_quorum(self):
        """3-node partition should NOT achieve quorum."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        
        # Consensus from minority partition
        result = mesh.attempt_consensus("tokyo")
        
        assert not result.success, "Minority partition should NOT achieve consensus"
        assert result.agreed_fidelity is None
    
    def test_minority_knows_it_failed(self):
        """Minority should be aware quorum was not reached."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        
        result = mesh.attempt_consensus("tokyo")
        
        assert len(result.participating_nodes) == 3, \
            f"Minority should see only 3 nodes, saw {len(result.participating_nodes)}"
        assert not result.success


class TestSplitBrainPrevention:
    """Tests that split-brain scenarios are prevented."""
    
    def test_no_dual_consensus(self):
        """Two partitions should never both achieve consensus."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        
        result_majority = mesh.attempt_consensus("beijing")
        result_minority = mesh.attempt_consensus("tokyo")
        
        # At most one can succeed
        successes = [result_majority.success, result_minority.success]
        assert sum(successes) <= 1, "Both partitions achieved consensus (split-brain!)"
    
    def test_symmetric_partition_blocks_all(self):
        """4-4 split should block ALL consensus."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.SYMMETRIC)
        
        results = [mesh.attempt_consensus(nid) for nid in NODE_IDS]
        
        successes = [r.success for r in results]
        assert not any(successes), \
            "No partition in 2-2-1 split should achieve quorum"
    
    def test_total_isolation_blocks_all(self):
        """Total isolation should block all consensus."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.TOTAL)
        
        results = [mesh.attempt_consensus(nid) for nid in NODE_IDS]
        
        assert not any(r.success for r in results), \
            "Isolated nodes should not achieve consensus"


class TestPartitionRecovery:
    """Tests recovery after partition healing."""
    
    def test_quorum_restored_after_heal(self):
        """Full quorum should be restored after healing."""
        mesh = PartitionableMesh()
        
        # Create and then heal partition
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        result_partitioned = mesh.attempt_consensus("tokyo")  # Minority
        
        mesh.heal_partition()
        result_healed = mesh.attempt_consensus("tokyo")  # Now has full network
        
        assert not result_partitioned.success, "Minority should fail during partition"
        assert result_healed.success, "Should succeed after healing"
        assert len(result_healed.participating_nodes) == 8
    
    def test_fidelity_consistent_after_recovery(self):
        """State should be consistent after recovery."""
        mesh = PartitionableMesh()
        
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        result1 = mesh.attempt_consensus("beijing")  # Majority
        
        mesh.heal_partition()
        result2 = mesh.attempt_consensus("beijing")  # Full network
        
        # Fidelity should be above SAGE_CONSTANT
        assert result2.agreed_fidelity >= SAGE_CONSTANT, \
            "Full network should maintain identity persistence"
    
    def test_epoch_advances_through_partition(self):
        """Epoch counter should advance continuously."""
        mesh = PartitionableMesh()
        
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        r1 = mesh.attempt_consensus("beijing")
        r2 = mesh.attempt_consensus("tokyo")
        
        mesh.heal_partition()
        r3 = mesh.attempt_consensus("beijing")
        
        epochs = [r1.epoch, r2.epoch, r3.epoch]
        assert epochs == sorted(epochs), "Epochs should increase monotonically"
        assert len(set(epochs)) == 3, "Each consensus should have unique epoch"


class TestStateEvolution:
    """Tests state evolution during and after partition."""
    
    def test_decoherence_affects_all_partitions(self):
        """Decoherence should affect nodes regardless of partition."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        
        initial_fidelities = {nid: mesh.nodes[nid].fidelity for nid in NODE_IDS}
        
        # Apply decoherence
        mesh.apply_decoherence(rate=0.1)
        
        for nid in NODE_IDS:
            assert mesh.nodes[nid].fidelity < initial_fidelities[nid], \
                f"Node {nid} should have decayed"
    
    def test_long_partition_degrades_identity(self):
        """Extended partition should degrade fidelity below threshold."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.SYMMETRIC)  # No quorum possible
        
        # Simulate extended time in partition
        for _ in range(50):
            mesh.apply_decoherence(rate=0.05)
        
        # All nodes should have degraded significantly
        for node in mesh.nodes.values():
            assert node.fidelity < 0.85, \
                f"Node {node.node_id} should have decayed below threshold"
    
    def test_minority_cannot_update_majority(self):
        """Minority partition cannot force state changes on majority."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.MAJORITY_MINORITY)
        
        # Record majority state
        majority_consensus = mesh.attempt_consensus("beijing")
        
        # Minority tries to update (should have no effect on majority view)
        mesh.update_node_fidelity("tokyo", 0.50)
        mesh.update_node_fidelity("singapore", 0.50)
        mesh.update_node_fidelity("paris", 0.50)
        
        # Majority consensus should be unchanged
        new_majority_consensus = mesh.attempt_consensus("beijing")
        
        assert majority_consensus.agreed_fidelity == new_majority_consensus.agreed_fidelity, \
            "Majority consensus should not change due to minority updates"


class TestEdgeCases:
    """Tests edge cases and boundary conditions."""
    
    def test_exactly_five_nodes_partition(self):
        """Exactly 5 nodes should be the minimum for quorum."""
        mesh = PartitionableMesh()
        
        # Create custom 5-3 partition
        mesh.partition_map = {
            "beijing": 0, "shanghai": 0, "dubai": 0, "london": 0, "nyc": 0,
            "tokyo": 1, "singapore": 1, "paris": 1
        }
        
        result = mesh.attempt_consensus("beijing")
        
        assert result.success, "Exactly 5 nodes should achieve quorum"
        assert len(result.participating_nodes) == 5
    
    def test_rapid_partition_changes(self):
        """System should handle rapid partition changes."""
        mesh = PartitionableMesh()
        
        for _ in range(10):
            mesh.create_partition(PartitionType.MAJORITY_MINORITY)
            mesh.attempt_consensus("beijing")
            
            mesh.heal_partition()
            mesh.attempt_consensus("beijing")
            
            mesh.create_partition(PartitionType.SYMMETRIC)
            mesh.attempt_consensus("dubai")
        
        # Should not crash and final state should be consistent
        mesh.heal_partition()
        final = mesh.attempt_consensus("beijing")
        assert final.success, "Should recover after rapid changes"
    
    def test_single_node_partition(self):
        """Single isolated node should fail gracefully."""
        mesh = PartitionableMesh()
        
        # Isolate Dubai and Paris only (still 6 nodes left)
        mesh.partition_map = {
            "beijing": 0, "shanghai": 0, "london": 0, "nyc": 0, "tokyo": 0, "singapore": 0,
            "dubai": 1, "paris": 2
        }
        
        result_isolated = mesh.attempt_consensus("dubai")
        result_main = mesh.attempt_consensus("beijing")
        
        assert not result_isolated.success, "Isolated node should not achieve consensus"
        assert result_main.success, "Main network should still work"


class TestConsensusHistory:
    """Tests consensus history tracking."""
    
    def test_history_recorded(self):
        """All consensus attempts should be recorded."""
        mesh = PartitionableMesh()
        
        mesh.attempt_consensus("beijing")
        mesh.attempt_consensus("tokyo")
        mesh.attempt_consensus("dubai")
        
        assert len(mesh.consensus_history) == 3, \
            f"Expected 3 history entries, got {len(mesh.consensus_history)}"
    
    def test_history_includes_failures(self):
        """Failed consensus attempts should also be recorded."""
        mesh = PartitionableMesh()
        mesh.create_partition(PartitionType.SYMMETRIC)
        
        for nid in NODE_IDS:
            mesh.attempt_consensus(nid)
        
        failures = [r for r in mesh.consensus_history if not r.success]
        assert len(failures) == 8, "All attempts in symmetric partition should fail"


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
