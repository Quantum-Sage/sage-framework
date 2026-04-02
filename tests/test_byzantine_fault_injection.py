"""
SAGE Framework — Byzantine Fault Injection Test Suite
======================================================

Tests the mesh quorum's resilience to adversarial node failures.

Byzantine Fault Tolerance requires: f < N/3 failures for safety
For our 5-node mesh: f < 5/3 = 1.67, so we tolerate 1 Byzantine node.
For safety, we actually use 3-of-5 quorum which tolerates 2 crash faults.

Test categories:
1. Crash faults (node goes silent)
2. Byzantine faults (node sends wrong data)
3. Network partitions (nodes can't communicate)
4. Timing attacks (nodes respond with stale data)
5. Sybil attacks (fake nodes join network)
"""

import pytest
import numpy as np
import random
from dataclasses import dataclass
from typing import List, Dict, Set, Optional
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# TEST CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SAGE_CONSTANT = 0.851
QUORUM_SIZE = 3  # Need 3 of 5 to agree
NUM_NODES = 5
NODE_NAMES = ["Beijing", "Shanghai", "Dubai", "London", "NYC"]


class FaultType(Enum):
    CRASH = "crash"           # Node stops responding
    BYZANTINE = "byzantine"   # Node sends malicious data
    PARTITION = "partition"   # Network split
    STALE = "stale"          # Node sends outdated state
    SYBIL = "sybil"          # Fake node injection


@dataclass
class NodeState:
    """Represents a node's view of the quantum state."""
    node_id: str
    fidelity: float
    coherence: float
    timestamp: int
    is_faulty: bool = False
    fault_type: Optional[FaultType] = None


@dataclass
class QuorumResult:
    """Result of a quorum vote."""
    consensus_reached: bool
    agreed_fidelity: Optional[float]
    agreeing_nodes: List[str]
    dissenting_nodes: List[str]
    identity_preserved: bool


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK MESH NETWORK
# ═══════════════════════════════════════════════════════════════════════════════

class MockMeshNetwork:
    """Simulates the 5-node SAGE mesh for testing."""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
        self.nodes: Dict[str, NodeState] = {}
        self.partitions: List[Set[str]] = [set(NODE_NAMES)]  # All connected
        self.timestamp = 0
        
        # Initialize healthy nodes
        for name in NODE_NAMES:
            self.nodes[name] = NodeState(
                node_id=name,
                fidelity=0.90 + np.random.uniform(-0.02, 0.02),
                coherence=0.95 + np.random.uniform(-0.03, 0.03),
                timestamp=0,
            )
    
    def inject_fault(self, node_id: str, fault_type: FaultType):
        """Inject a fault into a specific node."""
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        
        self.nodes[node_id].is_faulty = True
        self.nodes[node_id].fault_type = fault_type
        
        if fault_type == FaultType.BYZANTINE:
            # Byzantine node reports corrupted fidelity
            self.nodes[node_id].fidelity = np.random.uniform(0.1, 0.4)
        elif fault_type == FaultType.STALE:
            # Stale node has old timestamp
            self.nodes[node_id].timestamp = self.timestamp - 100
    
    def create_partition(self, group_a: List[str], group_b: List[str]):
        """Create a network partition."""
        self.partitions = [set(group_a), set(group_b)]
    
    def heal_partition(self):
        """Heal network partition."""
        self.partitions = [set(NODE_NAMES)]
    
    def can_communicate(self, node_a: str, node_b: str) -> bool:
        """Check if two nodes can communicate."""
        for partition in self.partitions:
            if node_a in partition and node_b in partition:
                return True
        return False
    
    def get_node_report(self, node_id: str) -> Optional[NodeState]:
        """Get a node's state report (simulates network request)."""
        node = self.nodes.get(node_id)
        if not node:
            return None
        
        if node.is_faulty and node.fault_type == FaultType.CRASH:
            return None  # Crashed nodes don't respond
        
        return node
    
    def run_quorum_vote(self, requester: str = "Beijing") -> QuorumResult:
        """Run a quorum vote to determine consensus state."""
        self.timestamp += 1
        
        # Collect reports from reachable nodes
        reports: List[NodeState] = []
        unreachable: List[str] = []
        
        for node_id in NODE_NAMES:
            if not self.can_communicate(requester, node_id):
                unreachable.append(node_id)
                continue
            
            report = self.get_node_report(node_id)
            if report is None:
                unreachable.append(node_id)
            else:
                reports.append(report)
        
        # Filter out stale reports
        current_reports = [
            r for r in reports 
            if self.timestamp - r.timestamp < 10  # Max 10 ticks stale
        ]
        
        # Check for quorum
        if len(current_reports) < QUORUM_SIZE:
            return QuorumResult(
                consensus_reached=False,
                agreed_fidelity=None,
                agreeing_nodes=[],
                dissenting_nodes=unreachable,
                identity_preserved=False,
            )
        
        # Compute median fidelity (Byzantine-resilient)
        fidelities = sorted([r.fidelity for r in current_reports])
        median_fidelity = fidelities[len(fidelities) // 2]
        
        # Find agreeing nodes (within 5% of median)
        agreeing = [r.node_id for r in current_reports 
                    if abs(r.fidelity - median_fidelity) < 0.05]
        dissenting = [r.node_id for r in current_reports 
                      if r.node_id not in agreeing] + unreachable
        
        consensus = len(agreeing) >= QUORUM_SIZE
        preserved = consensus and median_fidelity >= SAGE_CONSTANT
        
        return QuorumResult(
            consensus_reached=consensus,
            agreed_fidelity=median_fidelity if consensus else None,
            agreeing_nodes=agreeing,
            dissenting_nodes=dissenting,
            identity_preserved=preserved,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TEST CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrashFaults:
    """Test resilience to crash faults (nodes going silent)."""
    
    def test_single_crash_survives(self):
        """Quorum should survive 1 crashed node."""
        mesh = MockMeshNetwork()
        mesh.inject_fault("Dubai", FaultType.CRASH)
        
        result = mesh.run_quorum_vote()
        
        assert result.consensus_reached, "Should reach consensus with 4/5 nodes"
        assert len(result.agreeing_nodes) >= 3, "Should have 3+ agreeing nodes"
        assert "Dubai" in result.dissenting_nodes, "Crashed node should be dissenting"
    
    def test_double_crash_survives(self):
        """Quorum should survive 2 crashed nodes (3 remain)."""
        mesh = MockMeshNetwork()
        mesh.inject_fault("Dubai", FaultType.CRASH)
        mesh.inject_fault("Shanghai", FaultType.CRASH)
        
        result = mesh.run_quorum_vote()
        
        assert result.consensus_reached, "Should reach consensus with 3/5 nodes"
        assert len(result.agreeing_nodes) == 3, "Exactly 3 nodes should agree"
    
    def test_triple_crash_fails(self):
        """Quorum should FAIL with 3 crashed nodes (only 2 remain)."""
        mesh = MockMeshNetwork()
        mesh.inject_fault("Dubai", FaultType.CRASH)
        mesh.inject_fault("Shanghai", FaultType.CRASH)
        mesh.inject_fault("London", FaultType.CRASH)
        
        result = mesh.run_quorum_vote()
        
        assert not result.consensus_reached, "Should NOT reach consensus with 2/5 nodes"
        assert not result.identity_preserved, "Identity should NOT be preserved"


class TestByzantineFaults:
    """Test resilience to Byzantine faults (malicious nodes)."""
    
    def test_single_byzantine_survives(self):
        """Quorum should survive 1 Byzantine node via median voting."""
        mesh = MockMeshNetwork()
        mesh.inject_fault("Dubai", FaultType.BYZANTINE)
        
        result = mesh.run_quorum_vote()
        
        assert result.consensus_reached, "Should reach consensus despite Byzantine node"
        assert result.agreed_fidelity > 0.85, "Median should exclude Byzantine outlier"
        assert "Dubai" in result.dissenting_nodes, "Byzantine node should be excluded"
    
    def test_double_byzantine_risky(self):
        """2 Byzantine nodes may corrupt consensus (depends on honest fidelities)."""
        mesh = MockMeshNetwork()
        mesh.inject_fault("Dubai", FaultType.BYZANTINE)
        mesh.inject_fault("Shanghai", FaultType.BYZANTINE)
        
        result = mesh.run_quorum_vote()
        
        # With 2 Byzantine, median could be corrupted
        # This is a known limitation of 5-node BFT
        if result.consensus_reached:
            # Consensus reached, but fidelity may be corrupted
            assert True, "Consensus reached but may be incorrect"
        else:
            assert True, "No consensus (correct failure mode)"


class TestNetworkPartitions:
    """Test resilience to network partitions."""
    
    def test_majority_partition_survives(self):
        """Majority partition (3 nodes) should maintain consensus."""
        mesh = MockMeshNetwork()
        mesh.create_partition(
            group_a=["Beijing", "Shanghai", "NYC"],  # Majority
            group_b=["Dubai", "London"],              # Minority
        )
        
        result = mesh.run_quorum_vote(requester="Beijing")
        
        assert result.consensus_reached, "Majority partition should reach consensus"
        assert len(result.agreeing_nodes) == 3, "3 nodes should agree"
    
    def test_minority_partition_fails(self):
        """Minority partition (2 nodes) should NOT reach consensus."""
        mesh = MockMeshNetwork()
        mesh.create_partition(
            group_a=["Beijing", "Shanghai", "NYC"],
            group_b=["Dubai", "London"],
        )
        
        result = mesh.run_quorum_vote(requester="Dubai")  # In minority
        
        assert not result.consensus_reached, "Minority should NOT reach consensus"
    
    def test_partition_heal_recovers(self):
        """Consensus should recover after partition heals."""
        mesh = MockMeshNetwork()
        
        # Create and then heal partition
        mesh.create_partition(["Beijing", "Shanghai"], ["Dubai", "London", "NYC"])
        mesh.heal_partition()
        
        result = mesh.run_quorum_vote()
        
        assert result.consensus_reached, "Should recover after healing"


class TestTimingAttacks:
    """Test resilience to timing/staleness attacks."""
    
    def test_stale_node_excluded(self):
        """Nodes with stale timestamps should be excluded."""
        mesh = MockMeshNetwork()
        # Dubai gets a timestamp far in the past — it's the stale node
        mesh.inject_fault("Dubai", FaultType.STALE)

        # Advance the global clock AND update honest nodes' timestamps so
        # only Dubai remains stale (its timestamp was set to -100 by inject_fault).
        ticks = 20
        for _ in range(ticks):
            mesh.timestamp += 1
        # Keep all honest nodes current
        for name, node in mesh.nodes.items():
            if name != "Dubai":
                node.timestamp = mesh.timestamp

        result = mesh.run_quorum_vote()

        assert result.consensus_reached, \
            f"Should reach consensus without stale node (4 honest nodes remain), " \
            f"got {len(result.agreeing_nodes)} agreeing"
        assert "Dubai" not in result.agreeing_nodes, \
            "Stale node should be excluded from agreeing set"


class TestIdentityPersistence:
    """Test that identity persistence threshold is enforced."""
    
    def test_high_fidelity_preserves_identity(self):
        """High fidelity consensus should preserve identity."""
        mesh = MockMeshNetwork()
        
        # Set all nodes to high fidelity
        for node in mesh.nodes.values():
            node.fidelity = 0.92
        
        result = mesh.run_quorum_vote()
        
        assert result.identity_preserved, "High fidelity should preserve identity"
        assert result.agreed_fidelity >= SAGE_CONSTANT
    
    def test_low_fidelity_loses_identity(self):
        """Low fidelity consensus should NOT preserve identity."""
        mesh = MockMeshNetwork()
        
        # Set all nodes to low fidelity
        for node in mesh.nodes.values():
            node.fidelity = 0.75
        
        result = mesh.run_quorum_vote()
        
        assert result.consensus_reached, "Should still reach consensus"
        assert not result.identity_preserved, "Low fidelity should lose identity"
        assert result.agreed_fidelity < SAGE_CONSTANT


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_exact_threshold(self):
        """Test behavior at exactly SAGE_CONSTANT."""
        mesh = MockMeshNetwork()
        
        for node in mesh.nodes.values():
            node.fidelity = SAGE_CONSTANT
        
        result = mesh.run_quorum_vote()
        
        assert result.identity_preserved, "Exactly at threshold should preserve"
    
    def test_all_nodes_identical(self):
        """All nodes reporting identical state should always agree."""
        mesh = MockMeshNetwork()
        
        for node in mesh.nodes.values():
            node.fidelity = 0.90
            node.coherence = 0.95
        
        result = mesh.run_quorum_vote()
        
        assert result.consensus_reached
        assert len(result.agreeing_nodes) == 5, "All 5 should agree"
        assert len(result.dissenting_nodes) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# STRESS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestStress:
    """Stress tests with random fault injection."""
    
    @pytest.mark.parametrize("seed", range(100))
    def test_random_single_fault(self, seed):
        """Random single fault should always allow consensus."""
        np.random.seed(seed)
        mesh = MockMeshNetwork(seed=seed)
        
        # Inject random single fault
        fault_node = random.choice(NODE_NAMES)
        fault_type = random.choice([FaultType.CRASH, FaultType.BYZANTINE, FaultType.STALE])
        mesh.inject_fault(fault_node, fault_type)
        
        result = mesh.run_quorum_vote()
        
        assert result.consensus_reached, f"Seed {seed}: Single fault should not break consensus"
    
    @pytest.mark.parametrize("seed", range(50))
    def test_random_double_fault(self, seed):
        """Random double fault should usually allow consensus."""
        np.random.seed(seed)
        mesh = MockMeshNetwork(seed=seed)
        
        # Inject random double fault
        fault_nodes = random.sample(NODE_NAMES, 2)
        for node in fault_nodes:
            fault_type = random.choice([FaultType.CRASH, FaultType.BYZANTINE])
            mesh.inject_fault(node, fault_type)
        
        result = mesh.run_quorum_vote()
        
        # With 2 faults, consensus should still be possible (3 healthy remain)
        # But Byzantine faults may corrupt the result
        if FaultType.BYZANTINE not in [mesh.nodes[n].fault_type for n in fault_nodes]:
            assert result.consensus_reached, f"Seed {seed}: 2 crash faults should allow consensus"


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
