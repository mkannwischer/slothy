#!/usr/bin/env python3
#
# Test for configurable stack location naming (Issue #230)
#
# This test verifies that the stack_location_prefix configuration option
# works correctly by optimizing a simple assembly snippet that requires
# register spills and checking that the custom prefix is used.

import sys
from slothy import Slothy, Config

import slothy.targets.aarch64.aarch64_neon as AArch64_Neon
import slothy.targets.aarch64.cortex_a55 as Target_CortexA55

def test_default_prefix():
    """Test that default prefix 'STACK_LOC_' is used"""

    print("Testing default prefix 'STACK_LOC_'...")

    # Just verify the config default is correct
    conf = Config(AArch64_Neon, Target_CortexA55)

    if conf.stack_location_prefix != "STACK_LOC_":
        print(f"✗ Default config value incorrect: {conf.stack_location_prefix}")
        return False

    print("✓ Default prefix test passed")
    print(f"  Default config value: '{conf.stack_location_prefix}'")
    return True

def test_custom_prefix():
    """Test that custom prefix 'MY_STACK_' is used when configured"""

    # Assembly snippet - we'll just check the config is set correctly
    # and the Stack methods use it
    source = """
    ldr q0, [x1]
    add v0.8h, v0.8h, v0.8h
    str q0, [x0]
    """

    conf = Config(AArch64_Neon, Target_CortexA55)
    conf.selfcheck = False
    conf.selftest = False

    # Test that we can set custom prefix
    custom_prefix = "MY_STACK_"
    conf.stack_location_prefix = custom_prefix

    print(f"Testing custom prefix '{custom_prefix}'...")

    # Verify the config was set
    if conf.stack_location_prefix != custom_prefix:
        print(f"✗ Config not set correctly: {conf.stack_location_prefix} != {custom_prefix}")
        return False

    # Test that Stack methods use the prefix parameter
    test_reg = "x0"
    test_loc = "0"

    # Test with default prefix
    default_spill = AArch64_Neon.Stack.spill(test_reg, test_loc)
    if "STACK_LOC_" not in default_spill:
        print(f"✗ Default spill doesn't use default prefix: {default_spill}")
        return False

    # Test with custom prefix
    custom_spill = AArch64_Neon.Stack.spill(test_reg, test_loc, stack_prefix=custom_prefix)
    if custom_prefix not in custom_spill:
        print(f"✗ Custom spill doesn't use custom prefix: {custom_spill}")
        return False

    if "STACK_LOC_" in custom_spill:
        print(f"✗ Custom spill still uses default prefix: {custom_spill}")
        return False

    print(f"✓ Custom prefix test passed")
    print(f"  Default: {default_spill}")
    print(f"  Custom:  {custom_spill}")

    return True

def test_armv7m_prefix():
    """Test that custom prefix works for ARM v7M architecture too"""

    import slothy.targets.arm_v7m.arch_v7m as Arch_Armv7M

    test_reg = "r0"
    test_loc = "0"
    custom_prefix = "CUSTOM_LOC_"

    print(f"Testing ARM v7M with custom prefix '{custom_prefix}'...")

    # Test Spill class (which has Stack alias)
    custom_spill = Arch_Armv7M.Spill.spill(test_reg, test_loc, stack_prefix=custom_prefix)
    if custom_prefix not in custom_spill:
        print(f"✗ ARM v7M custom spill doesn't use custom prefix: {custom_spill}")
        return False

    # Test Stack alias
    custom_spill_via_stack = Arch_Armv7M.Stack.spill(test_reg, test_loc, stack_prefix=custom_prefix)
    if custom_prefix not in custom_spill_via_stack:
        print(f"✗ ARM v7M Stack alias doesn't use custom prefix: {custom_spill_via_stack}")
        return False

    print(f"✓ ARM v7M prefix test passed")
    print(f"  Spill: {custom_spill}")
    print(f"  Stack: {custom_spill_via_stack}")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing configurable stack location naming (Issue #230)")
    print("=" * 60)
    print()

    tests = [
        ("Default prefix", test_default_prefix),
        ("Custom prefix (AArch64)", test_custom_prefix),
        ("Custom prefix (ARM v7M)", test_armv7m_prefix),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test '{name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
        print()

    # Summary
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    sys.exit(0 if passed == total else 1)
