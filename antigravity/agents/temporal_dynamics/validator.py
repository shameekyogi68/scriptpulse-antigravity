#!/usr/bin/env python3
"""
Temporal Dynamics Validator

Validates temporal dynamics output for stability, determinism, and
absence of runaway accumulation or single-scene dominance.
"""

import json
import sys
import math
from pathlib import Path
from typing import List, Dict


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_bounded_signals(signals: List[Dict]) -> None:
    """Validate that S values don't exhibit runaway accumulation"""
    max_signal = max(s['attentional_signal'] for s in signals)
    
    # Reasonable upper bound (allow some flexibility)
    if max_signal > 10.0:
        raise ValidationError(
            f"Runaway accumulation detected: max S = {max_signal:.2f} (should be < 10.0)"
        )
    
    print(f"  Max attentional signal: {max_signal:.2f} (bounded ✓)")


def validate_no_single_scene_dominance(signals: List[Dict]) -> None:
    """Validate that no single scene causes excessive signal spike"""
    for i in range(1, len(signals)):
        prev_signal = signals[i-1]['attentional_signal']
        curr_signal = signals[i]['attentional_signal']
        
        # Check for unreasonable single-scene jumps
        jump = curr_signal - prev_signal
        
        # Allow jumps up to 2x the instantaneous effort
        max_reasonable_jump = 2.0 * signals[i]['instantaneous_effort']
        
        if jump > max_reasonable_jump + 1.0:  # +1.0 tolerance
            raise ValidationError(
                f"Scene {signals[i]['scene_index']}: Single-scene dominance detected. "
                f"Signal jumped {jump:.2f} (from {prev_signal:.2f} to {curr_signal:.2f})"
            )
    
    print(f"  No single-scene dominance detected ✓")


def validate_determinism(signals: List[Dict]) -> None:
    """Validate signal values are deterministic (no NaN/Inf)"""
    for signal in signals:
        scene_idx = signal['scene_index']
        
        for key in ['instantaneous_effort', 'attentional_signal', 'recovery_credit']:
            value = signal[key]
            
            if math.isnan(value):
                raise ValidationError(
                    f"Scene {scene_idx}: {key} is NaN"
                )
            
            if math.isinf(value):
                raise ValidationError(
                    f"Scene {scene_idx}: {key} is infinite"
                )
    
    print(f"  All signals deterministic (no NaN/Inf) ✓")


def validate_recovery_bounds(signals: List[Dict]) -> None:
    """Validate recovery credits are properly bounded"""
    R_MAX = 0.5  # From temporal engine
    
    for signal in signals:
        recovery = signal['recovery_credit']
        
        if recovery < 0:
            raise ValidationError(
                f"Scene {signal['scene_index']}: Negative recovery {recovery:.3f}"
            )
        
        if recovery > R_MAX + 0.01:  # Small tolerance for rounding
            raise ValidationError(
                f"Scene {signal['scene_index']}: Recovery {recovery:.3f} exceeds maximum {R_MAX}"
            )
    
    print(f"  Recovery credits properly bounded [0, {R_MAX}] ✓")


def validate_fatigue_states(signals: List[Dict]) -> None:
    """Validate fatigue state classifications"""
    valid_states = ["normal", "elevated", "high", "extreme"]
    
    for signal in signals:
        state = signal['fatigue_state']
        
        if state not in valid_states:
            raise ValidationError(
                f"Scene {signal['scene_index']}: Invalid fatigue state '{state}'"
            )
    
    # Count state distribution
    state_counts = {s: 0 for s in valid_states}
    for signal in signals:
        state_counts[signal['fatigue_state']] += 1
    
    print(f"  Fatigue state distribution:")
    for state, count in state_counts.items():
        if count > 0:
            pct = 100 * count / len(signals)
            print(f"    {state}: {count} ({pct:.1f}%)")


def validate_opening_buffer(signals: List[Dict]) -> None:
    """Validate that opening scenes don't have unreasonable spikes"""
    if len(signals) < 5:
        return  # Too short to validate
    
    # Check first 5 scenes for stability
    first_five_signals = [s['attentional_signal'] for s in signals[:5]]
    max_early = max(first_five_signals)
    
    # Early scenes should have lower accumulation due to buffer
    overall_max = max(s['attentional_signal'] for s in signals)
    
    if max_early > overall_max * 0.9:
        print(f"  ⚠️  Warning: Early scenes have high signal ({max_early:.2f} vs max {overall_max:.2f})")
    else:
        print(f"  Opening buffer effective (early max {max_early:.2f} < overall {overall_max:.2f}) ✓")


def check_for_drift(signals: List[Dict]) -> None:
    """Check for systematic drift in signal over time"""
    if len(signals) < 10:
        return  # Too short to detect drift
    
    # Simple linear regression to detect drift
    # If slope is too high, might indicate accumulation without recovery
    n = len(signals)
    x_values = list(range(n))
    y_values = [s['attentional_signal'] for s in signals]
    
    # Calculate slope
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n
    
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    
    if denominator > 0:
        slope = numerator / denominator
        
        # Positive slope is expected, but not too steep
        if slope > 0.05:  # Arbitrary threshold
            print(f"  ⚠️  Warning: Positive drift detected (slope={slope:.4f})")
        else:
            print(f"  No significant drift (slope={slope:.4f}) ✓")


def main():
    """Main validation entry point"""
    if len(sys.argv) != 2:
        print("Usage: python validator.py <temporal_dynamics_json>")
        print("\nValidates temporal dynamics output from temporal_engine.py")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    
    try:
        # Load temporal dynamics
        data = json.loads(json_file.read_text())
        signals = data.get('temporal_signals', [])
        
        if not signals:
            raise ValidationError("No temporal signals found in output")
        
        print(f"✓ Loaded temporal dynamics: {len(signals)} scenes")
        
        # Run validations
        print("\nRunning validations...")
        
        print("  • Checking bounded signals...", end=' ')
        validate_bounded_signals(signals)
        
        print("  • Checking single-scene dominance...", end=' ')
        validate_no_single_scene_dominance(signals)
        
        print("  • Checking determinism...", end=' ')
        validate_determinism(signals)
        
        print("  • Checking recovery bounds...", end=' ')
        validate_recovery_bounds(signals)
        
        print("  • Checking fatigue states...")
        validate_fatigue_states(signals)
        
        print("  • Checking opening buffer...", end=' ')
        validate_opening_buffer(signals)
        
        print("  • Checking for drift...", end=' ')
        check_for_drift(signals)
        
        # Print summary statistics
        print(f"\n✓ Summary statistics:")
        
        efforts = [s['instantaneous_effort'] for s in signals]
        s_values = [s['attentional_signal'] for s in signals]
        recoveries = [s['recovery_credit'] for s in signals]
        
        print(f"    Instantaneous effort: mean={sum(efforts)/len(efforts):.3f}, "
              f"max={max(efforts):.3f}")
        print(f"    Attentional signal: mean={sum(s_values)/len(s_values):.3f}, "
              f"max={max(s_values):.3f}")
        print(f"    Recovery credit: mean={sum(recoveries)/len(recoveries):.3f}, "
              f"max={max(recoveries):.3f}")
        
        print("\n✅ All validations passed!")
        
    except ValidationError as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
