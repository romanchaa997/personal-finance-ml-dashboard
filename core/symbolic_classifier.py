"""Symbolic AI Classifier with Symbiotic Learning Principles

This module implements symbolic AI reasoning combined with neuro-symbolic
approaches for financial transaction classification. It uses symbiotic learning
principles where symbolic rules and neural networks cooperate.
"""

import logging
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TransactionSymbol(Enum):
    """Symbolic representations of transaction types"""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"
    INVESTMENT = "INVESTMENT"
    SAVINGS = "SAVINGS"
    DEBT = "DEBT"
    TAX = "TAX"
    UTILITY = "UTILITY"


class RiskSymbol(Enum):
    """Symbolic risk classifications"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class SymbolicRule:
    """Defines a symbolic rule for transaction classification"""
    name: str
    condition: callable
    classification: TransactionSymbol
    confidence: float = 0.8
    priority: int = 1


class SymbolicClassifier:
    """Symbiotic classifier using symbolic reasoning and neural networks"""

    def __init__(self):
        self.rules: List[SymbolicRule] = []
        self.symbol_memory: Dict[str, TransactionSymbol] = {}
        self.confidence_threshold = 0.7
        self._initialize_rules()
        logger.info("Symbolic Classifier initialized with symbiotic principles")

    def _initialize_rules(self):
        """Initialize symbolic rules for common transaction patterns"""
        # Income rules
        self.add_rule(SymbolicRule(
            name="salary_income",
            condition=lambda t: "salary" in t.get("description", "").lower(),
            classification=TransactionSymbol.INCOME,
            confidence=0.95,
            priority=1
        ))

        # Expense rules
        self.add_rule(SymbolicRule(
            name="grocery_expense",
            condition=lambda t: any(x in t.get("merchant", "").lower() 
                                    for x in ["grocery", "supermarket", "market"]),
            classification=TransactionSymbol.EXPENSE,
            confidence=0.9,
            priority=2
        ))

        self.add_rule(SymbolicRule(
            name="utility_expense",
            condition=lambda t: any(x in t.get("description", "").lower() 
                                    for x in ["electric", "water", "gas", "internet"]),
            classification=TransactionSymbol.UTILITY,
            confidence=0.92,
            priority=2
        ))

        # Transfer rules
        self.add_rule(SymbolicRule(
            name="internal_transfer",
            condition=lambda t: t.get("type") == "transfer" and t.get("amount", 0) > 0,
            classification=TransactionSymbol.TRANSFER,
            confidence=0.98,
            priority=1
        ))

        # Investment rules
        self.add_rule(SymbolicRule(
            name="investment_expense",
            condition=lambda t: any(x in t.get("merchant", "").lower() 
                                    for x in ["broker", "exchange", "investment", "etf"]),
            classification=TransactionSymbol.INVESTMENT,
            confidence=0.85,
            priority=3
        ))

    def add_rule(self, rule: SymbolicRule):
        """Add a symbolic rule to the classifier"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: (-r.priority, -r.confidence))

    def classify_symbolic(self, transaction: Dict[str, Any]) -> Tuple[TransactionSymbol, float]:
        """Classify transaction using symbolic rules"""
        for rule in self.rules:
            try:
                if rule.condition(transaction):
                    self.symbol_memory[transaction.get("id", "unknown")] = rule.classification
                    logger.debug(f"Rule '{rule.name}' matched with confidence {rule.confidence}")
                    return rule.classification, rule.confidence
            except Exception as e:
                logger.warning(f"Error applying rule {rule.name}: {e}")
                continue
        
        return TransactionSymbol.EXPENSE, 0.5  # Default classification

    def apply_symbiotic_learning(self, transaction: Dict[str, Any], 
                                neural_prediction: Tuple[TransactionSymbol, float]) -> Tuple[TransactionSymbol, float]:
        """Symbiotic learning: combines symbolic and neural predictions"""
        symbolic_pred, symbolic_conf = self.classify_symbolic(transaction)
        neural_pred, neural_conf = neural_prediction

        # Symbiotic fusion: weight predictions based on confidence
        if abs(symbolic_conf - neural_conf) < 0.15:  # Agreement zone
            # Both models agree, increase confidence
            fused_conf = min(1.0, (symbolic_conf + neural_conf) / 1.5)
            final_pred = symbolic_pred
        else:  # Disagreement zone
            # Use higher confidence model
            if symbolic_conf > neural_conf:
                final_pred = symbolic_pred
                fused_conf = symbolic_conf * 0.95  # Slight penalty for disagreement
            else:
                final_pred = neural_pred
                fused_conf = neural_conf * 0.95

        logger.info(f"Symbiotic prediction: {final_pred.value} (confidence: {fused_conf:.2f})")
        return final_pred, fused_conf

    def extract_symbolic_features(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Extract symbolic features from transaction"""
        classification, conf = self.classify_symbolic(transaction)
        
        return {
            "symbol": classification.value,
            "symbol_confidence": conf,
            "matched_rules": [r.name for r in self.rules if r.condition(transaction)],
            "risk_level": self._assess_risk_symbolic(transaction, classification)
        }

    def _assess_risk_symbolic(self, transaction: Dict[str, Any], 
                             classification: TransactionSymbol) -> RiskSymbol:
        """Assess transaction risk using symbolic reasoning"""
        amount = abs(transaction.get("amount", 0))
        
        if classification == TransactionSymbol.INVESTMENT:
            if amount > 10000:
                return RiskSymbol.HIGH
            elif amount > 5000:
                return RiskSymbol.MEDIUM
        
        elif classification == TransactionSymbol.TRANSFER:
            if amount > 50000:
                return RiskSymbol.CRITICAL
            elif amount > 20000:
                return RiskSymbol.HIGH
        
        elif classification == TransactionSymbol.DEBT:
            return RiskSymbol.HIGH
        
        return RiskSymbol.LOW

    def batch_classify(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch classify multiple transactions"""
        results = []
        for transaction in transactions:
            features = self.extract_symbolic_features(transaction)
            results.append({**transaction, **features})
        return results
