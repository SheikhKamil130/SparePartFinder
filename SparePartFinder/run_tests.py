"""
Test Runner Script for SparePartFinder Pro
Runs all test suites and generates a summary report
"""
import subprocess
import sys
import time

def run_tests():
    """Run all test suites"""
    print("="*70)
    print("SparePartFinder Pro - Test Suite")
    print("="*70)
    
    start_time = time.time()
    
    # Run pytest with verbose output
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=False,
            text=True
        )
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"Testing completed in {elapsed_time:.2f} seconds")
        print("="*70)
        
        if result.returncode == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print("⚠️  SOME TESTS FAILED - Check output above for details")
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def run_tests_with_coverage():
    """Run tests with coverage report"""
    print("="*70)
    print("SparePartFinder Pro - Test Suite with Coverage")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--cov=.", "--cov-report=term-missing"],
            capture_output=False,
            text=True
        )
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests with coverage: {e}")
        return 1

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run SparePartFinder tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    args = parser.parse_args()
    
    if args.coverage:
        exit_code = run_tests_with_coverage()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)
