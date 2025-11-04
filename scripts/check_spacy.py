"""Check if spaCy is installed and working"""
import sys

print("=" * 60)
print("Checking spaCy Installation")
print("=" * 60)
print()

# Check if spaCy is installed
try:
    import spacy
    print("[OK] spaCy is INSTALLED")
    print(f"     Version: {spacy.__version__}")
    print()
    
    # Check if English model is available
    try:
        nlp = spacy.load("en_core_web_sm")
        print("[OK] English model (en_core_web_sm) is LOADED")
        print("     spaCy is fully functional!")
        print()
        
        # Test it
        doc = nlp("This is a test sentence.")
        print("[OK] spaCy NLP processing works!")
        print(f"     Processed: {len(list(doc))} tokens")
        print()
        print("=" * 60)
        print("RESULT: spaCy is FULLY INSTALLED AND WORKING")
        print("=" * 60)
        
    except OSError as e:
        print("[WARNING] English model not found")
        print(f"     Error: {e}")
        print()
        print("To install the model, run:")
        print("  python -m spacy download en_core_web_sm")
        print()
        print("=" * 60)
        print("RESULT: spaCy installed but model missing")
        print("=" * 60)
        
except ImportError:
    print("[NOT INSTALLED] spaCy is not installed")
    print()
    print("To install spaCy, run:")
    print("  python -m pip install spacy")
    print()
    print("Note: spaCy requires C++ Build Tools on Windows")
    print("Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    print()
    print("=" * 60)
    print("RESULT: spaCy is NOT INSTALLED")
    print("=" * 60)

# Check in application
print()
print("Checking application integration...")
try:
    from app.services.ai_parser import HAS_SPACY, AIParser
    print(f"HAS_SPACY flag: {HAS_SPACY}")
    
    ap = AIParser()
    print("AIParser initialized")
    
    if ap.nlp is not None:
        print("NLP model loaded in AIParser: YES")
        print("spaCy is working in the application!")
    else:
        print("NLP model loaded in AIParser: NO")
        print("Using basic parsing mode (no spaCy)")
        
except Exception as e:
    print(f"Error checking application: {e}")



