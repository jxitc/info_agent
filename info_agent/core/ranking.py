"""
Enhanced Ranking and Fusion for Info Agent

Implements advanced ranking algorithms including Reciprocal Rank Fusion (RRF),
adaptive thresholding, and confidence scoring for multi-source search results.
"""

import math
import logging
from typing import List, Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from info_agent.core.models import MemorySearchResult
from info_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SearchSource:
    """Represents a search source with its characteristics"""
    name: str
    weight: float = 1.0
    reliability: float = 1.0  # 0.0 to 1.0
    preferred_for: List[str] = None  # Query types this source excels at


@dataclass 
class RankingMetrics:
    """Detailed ranking metrics for transparency"""
    rrf_score: float
    original_score: float
    confidence: float
    source_diversity: float
    rank_in_source: int
    explanation: str
    contributing_sources: List[str]


# Removed QueryCharacteristics - using simple threshold-based filtering instead


class EnhancedRanker:
    """
    Enhanced ranking system with RRF, adaptive thresholds, and transparency.
    """
    
    # Source configurations
    SEARCH_SOURCES = {
        'structured': SearchSource(
            name='structured',
            weight=1.0,
            reliability=0.95,
            preferred_for=['specific', 'exact', 'entity']
        ),
        'semantic': SearchSource(
            name='semantic', 
            weight=1.2,
            reliability=0.85,
            preferred_for=['conceptual', 'general', 'thematic']
        ),
        'hybrid': SearchSource(
            name='hybrid',
            weight=1.1,
            reliability=0.90,
            preferred_for=['complex', 'multi-faceted']
        )
    }
    
    # RRF parameter (lower values give more importance to top ranks)
    RRF_K = 60  # Standard value used in many systems
    
    def __init__(self):
        """Initialize the enhanced ranker"""
        self.logger = get_logger(__name__)
        
    # Query analysis removed - using simple threshold-based filtering instead
    # TODO: Consider LLM-based query analysis for future improvements
        
    def reciprocal_rank_fusion(self, 
                              source_results: Dict[str, List[MemorySearchResult]],
                              source_weights: Optional[Dict[str, float]] = None,
                              k: int = None) -> List[Tuple[MemorySearchResult, RankingMetrics]]:
        """
        Apply Reciprocal Rank Fusion to combine results from multiple sources.
        
        Args:
            source_results: Dict mapping source names to their ranked results
            source_weights: Optional weights for each source
            k: RRF parameter (default: self.RRF_K)
            
        Returns:
            List of (result, metrics) tuples sorted by RRF score
        """
        k = k or self.RRF_K
        source_weights = source_weights or {}
        
        # Calculate RRF scores for all unique memories
        rrf_scores = defaultdict(float)
        memory_data = {}  # Store original results and metadata
        source_contributions = defaultdict(list)
        
        for source_name, results in source_results.items():
            source_weight = source_weights.get(source_name, self.SEARCH_SOURCES.get(source_name, SearchSource(source_name)).weight)
            
            self.logger.info(f"Processing {len(results)} results from '{source_name}' (weight: {source_weight:.2f})")
            
            for rank, result in enumerate(results, 1):
                memory_id = result.memory.id
                
                # Calculate RRF contribution: weight / (k + rank)
                rrf_contribution = source_weight / (k + rank)
                rrf_scores[memory_id] += rrf_contribution
                
                # Store result data and metadata
                if memory_id not in memory_data:
                    memory_data[memory_id] = {
                        'result': result,
                        'original_scores': {},
                        'ranks_in_sources': {},
                        'sources': set()
                    }
                
                memory_data[memory_id]['original_scores'][source_name] = getattr(result, 'relevance_score', 1.0)
                memory_data[memory_id]['ranks_in_sources'][source_name] = rank
                memory_data[memory_id]['sources'].add(source_name)
                source_contributions[memory_id].append(f"{source_name}:rank{rank}")
        
        # Create final ranked results with detailed metrics
        final_results = []
        sorted_memories = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        self.logger.info(f"RRF computed scores for {len(sorted_memories)} unique memories")
        
        for memory_id, rrf_score in sorted_memories:
            data = memory_data[memory_id]
            result = data['result']
            
            # Calculate confidence based on source agreement and scores
            confidence = self._calculate_confidence(
                sources=data['sources'],
                original_scores=data['original_scores'],
                ranks=data['ranks_in_sources']
            )
            
            # Calculate source diversity (higher = found in more diverse sources)
            source_diversity = len(data['sources']) / len(source_results)
            
            # Get best original rank for reference
            best_rank = min(data['ranks_in_sources'].values())
            best_score = max(data['original_scores'].values()) if data['original_scores'] else 0.0
            
            # Create explanation
            source_list = sorted(data['sources'])
            explanation = f"Found in {len(source_list)} sources: {', '.join(source_list)}. RRF score: {rrf_score:.4f}"
            
            metrics = RankingMetrics(
                rrf_score=rrf_score,
                original_score=best_score,
                confidence=confidence,
                source_diversity=source_diversity,
                rank_in_source=best_rank,
                explanation=explanation,
                contributing_sources=source_list
            )
            
            # Update result with new scoring
            result.relevance_score = rrf_score
            result.match_type = "rrf_fused" if len(data['sources']) > 1 else f"rrf_{list(data['sources'])[0]}"
            
            final_results.append((result, metrics))
        
        # Log top results for debugging
        self.logger.info(f"Top RRF results:")
        for i, (result, metrics) in enumerate(final_results[:3], 1):
            self.logger.info(f"  {i}. Memory {result.memory.id}: RRF={metrics.rrf_score:.4f}, "
                           f"Confidence={metrics.confidence:.2f}, Sources={len(metrics.contributing_sources)}")
        
        return final_results
    
    def _calculate_confidence(self, 
                             sources: Set[str], 
                             original_scores: Dict[str, float], 
                             ranks: Dict[str, int]) -> float:
        """
        Calculate confidence score based on source agreement and original scores.
        
        Args:
            sources: Set of source names that found this result
            original_scores: Original scores from each source
            ranks: Rank position in each source
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from number of sources
        source_confidence = min(len(sources) / len(self.SEARCH_SOURCES), 1.0)
        
        # Score consistency (lower variance = higher confidence)
        if len(original_scores) > 1:
            scores = list(original_scores.values())
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            score_consistency = max(0.0, 1.0 - variance)
        else:
            score_consistency = 1.0 if original_scores else 0.5
        
        # Rank consistency (higher ranks = lower confidence penalty)
        rank_confidence = 1.0
        if ranks:
            avg_rank = sum(ranks.values()) / len(ranks)
            rank_confidence = max(0.1, 1.0 - (avg_rank - 1) * 0.1)  # Penalty for lower ranks
        
        # Source reliability weighting
        reliability_weight = 0.0
        total_weight = 0.0
        for source in sources:
            source_config = self.SEARCH_SOURCES.get(source, SearchSource(source))
            reliability_weight += source_config.reliability
            total_weight += 1.0
        avg_reliability = reliability_weight / max(total_weight, 1.0)
        
        # Combine factors
        confidence = (source_confidence * 0.3 + 
                     score_consistency * 0.3 + 
                     rank_confidence * 0.2 +
                     avg_reliability * 0.2)
        
        return max(0.0, min(1.0, confidence))
    
    def apply_threshold_filter(self, 
                             results: List[Tuple[MemorySearchResult, RankingMetrics]],
                             threshold: float = 0.01) -> List[Tuple[MemorySearchResult, RankingMetrics]]:
        """
        Apply simple threshold filtering.
        
        Args:
            results: List of (result, metrics) tuples
            threshold: Minimum RRF score threshold
            
        Returns:
            Filtered list of results above threshold
        """
        # Apply threshold filtering
        filtered_results = []
        for result, metrics in results:
            # Use RRF score for threshold
            if metrics.rrf_score >= threshold:
                filtered_results.append((result, metrics))
            else:
                self.logger.debug(f"Filtered out Memory {result.memory.id}: "
                                f"rrf_score={metrics.rrf_score:.3f} < threshold={threshold:.3f}")
        
        self.logger.info(f"Threshold {threshold:.3f} filtered {len(results) - len(filtered_results)} results "
                        f"(kept {len(filtered_results)}/{len(results)})")
        
        return filtered_results
    
    def deduplicate_and_diversify(self, 
                                 results: List[Tuple[MemorySearchResult, RankingMetrics]],
                                 max_results: int) -> List[Tuple[MemorySearchResult, RankingMetrics]]:
        """
        Remove duplicates and promote source diversity in final results.
        
        Args:
            results: List of (result, metrics) tuples
            max_results: Maximum number of results to return
            
        Returns:
            Deduplicated and diversified results
        """
        if len(results) <= max_results:
            return results
        
        # Results are already unique by memory_id from RRF, but we may want to promote diversity
        seen_contents = set()
        diversified_results = []
        source_counts = defaultdict(int)
        
        for result, metrics in results:
            # Simple content-based deduplication (first 100 characters)
            content_signature = result.memory.content[:100].strip().lower()
            
            if content_signature not in seen_contents:
                # Promote source diversity - slight penalty for over-represented sources
                diversity_bonus = 1.0
                for source in metrics.contributing_sources:
                    source_count = source_counts[source]
                    if source_count > max_results // 3:  # If source has > 1/3 of results
                        diversity_bonus *= 0.95  # Small penalty
                
                # Apply diversity bonus to score
                result.relevance_score *= diversity_bonus
                
                diversified_results.append((result, metrics))
                seen_contents.add(content_signature)
                
                # Update source counts
                for source in metrics.contributing_sources:
                    source_counts[source] += 1
                    
                if len(diversified_results) >= max_results:
                    break
        
        # Re-sort after diversity adjustments
        diversified_results.sort(key=lambda x: x[0].relevance_score, reverse=True)
        
        self.logger.info(f"Diversification kept {len(diversified_results)} unique results")
        if len(diversified_results) < len(results):
            self.logger.debug(f"Source distribution: {dict(source_counts)}")
        
        return diversified_results[:max_results]
    
    def rank_search_results(self,
                           source_results: Dict[str, List[MemorySearchResult]], 
                           query: str,
                           max_results: int = 20) -> List[MemorySearchResult]:
        """
        Complete ranking pipeline: apply RRF, filter, and diversify.
        
        Args:
            source_results: Dict mapping source names to their results
            query: Original search query
            max_results: Maximum number of final results
            
        Returns:
            Final ranked and filtered list of MemorySearchResult objects
        """
        self.logger.info(f"Starting enhanced ranking for query: '{query}'")
        self.logger.info(f"Input sources: {list(source_results.keys())} with total {sum(len(r) for r in source_results.values())} results")
        
        # Step 1: Use standard source weights (no query-specific analysis)
        source_weights = {}
        for source_name in source_results.keys():
            source_weights[source_name] = self.SEARCH_SOURCES.get(source_name, SearchSource(source_name)).weight
        
        # Step 2: Apply Reciprocal Rank Fusion
        rrf_results = self.reciprocal_rank_fusion(source_results, source_weights)
        
        # Step 3: Apply standard threshold filtering
        filtered_results = self.apply_threshold_filter(rrf_results, threshold=0.01)
        
        # Step 4: Deduplicate and promote diversity
        final_results = self.deduplicate_and_diversify(filtered_results, max_results)
        
        # Step 5: Extract MemorySearchResult objects and add ranking explanations
        ranked_memories = []
        for result, metrics in final_results:
            # Add ranking explanation to the result for UI transparency
            result.ranking_explanation = (
                f"RRF Score: {metrics.rrf_score:.3f} | "
                f"Confidence: {metrics.confidence:.2f} | "
                f"Sources: {', '.join(metrics.contributing_sources)}"
            )
            ranked_memories.append(result)
        
        self.logger.info(f"Enhanced ranking complete: {len(ranked_memories)} final results")
        return ranked_memories


# Global ranker instance
_enhanced_ranker: Optional[EnhancedRanker] = None


def get_enhanced_ranker() -> EnhancedRanker:
    """Get global enhanced ranker instance (singleton pattern)"""
    global _enhanced_ranker
    if _enhanced_ranker is None:
        _enhanced_ranker = EnhancedRanker()
    return _enhanced_ranker
