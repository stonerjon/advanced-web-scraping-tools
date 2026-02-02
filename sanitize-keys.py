#!/home/kingofpirates/scripts/venv/bin/python3
import re
import sys
import argparse
import shutil
from pathlib import Path

# Known API key patterns
KNOWN_PATTERNS = [
    # OpenAI (sk-..., sk-proj-..., sk-admin-...)
    (r'sk-[a-zA-Z0-9_-]{20,}', '[REDACTED-OPENAI-KEY]'),
    # AWS Access Key ID
    (r'AKIA[0-9A-Z]{16}', '[REDACTED-AWS-KEY]'),
    # AWS Secret (verbose warning since it's just random base64)
    (r'(?:AWS_SECRET_ACCESS_KEY|aws_secret_access_key)\s*[=:]\s*[A-Za-z0-9/+=]{40}', '[REDACTED-AWS-SECRET]'),
    # Google API (AIza...)
    (r'AIza[0-9A-Za-z_-]{35}', '[REDACTED-GOOGLE-KEY]'),
    # GitHub Personal Access Token
    (r'ghp_[a-zA-Z0-9]{36}', '[REDACTED-GITHUB-KEY]'),
    (r'gho_[a-zA-Z0-9]{36}', '[REDACTED-GITHUB-OAUTH]'),
    (r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}', '[REDACTED-GITHUB-PAT]'),
    # Slack
    (r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*', '[REDACTED-SLACK-TOKEN]'),
    # Stripe
    (r'sk_(live|test)_[0-9a-zA-Z]{24,}', '[REDACTED-STRIPE-KEY]'),
    # Twilio
    (r'AC[a-f0-9]{32}', '[REDACTED-TWILIO-SID]'),
    (r'SK[a-f0-9]{32}', '[REDACTED-TWILIO-KEY]'),
    # SendGrid
    (r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}', '[REDACTED-SENDGRID-KEY]'),
    # Mailgun
    (r'key-[0-9a-f]{32}', '[REDACTED-MAILGUN-KEY]'),
    # Heroku
    (r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '[REDACTED-UUID/HEROKU]'),
    # Generic Bearer tokens in headers
    (r'(?i)(authorization:\s*bearer\s+)[a-zA-Z0-9_\-\.=]+', r'\1[REDACTED-BEARER]'),
    # Generic API Key assignments (key="...", api_key=..., etc)
    (r'(?i)((?:api[_-]?key|apikey|secret[_-]?key|auth[_-]?token)\s*[=:]\s*)["\']?[a-zA-Z0-9_\-]{20,}["\']?', r'\1[REDACTED-KEY]'),
]

# Generic high-entropy detector (catches keys without known prefixes)
# Looks for 32+ character hex or base64-like strings in suspicious contexts
GENERIC_PATTERNS = [
    # Hex strings 32+ chars (common for secrets) when labeled as key/secret/token
    (r'(?i)((?:secret|password|token|key)\s*[=:]\s*["\']?)[a-f0-9]{32,}["\']?', r'\1[REDACTED-HEX]'),
    # Base64-looking strings 40+ chars in key contexts (ends with = or alphanumeric + /)
    (r'(?i)((?:secret|password|token|key)\s*[=:]\s*["\']?)[A-Za-z0-9+/]{40,}=?["\']?', r'\1[REDACTED-B64]'),
]

def sanitize_text(text, aggressive=False):
    """Remove API keys from text."""
    original = text
    
    # Apply known patterns
    for pattern, replacement in KNOWN_PATTERNS:
        text = re.sub(pattern, replacement, text)
    
    # Apply generic patterns only if aggressive mode (avoid false positives)
    if aggressive:
        for pattern, replacement in GENERIC_PATTERNS:
            text = re.sub(pattern, replacement, text)
            
        # Ultra-aggressive: any 40+ char alphanumeric that looks random (high entropy)
        # This might catch passwords too, hence "aggressive" mode only
        def replace_random(match):
            s = match.group(0)
            # Skip if it's obviously a word (lowercase only) or URL component
            if s.islower() and re.match(r'^[a-z]+$', s):
                return s
            # Check entropy (roughly): if it has digits, upper, lower, and symbols
            has_digit = bool(re.search(r'\d', s))
            has_upper = bool(re.search(r'[A-Z]', s))
            has_lower = bool(re.search(r'[a-z]', s))
            if has_digit and has_upper and len(s) > 40:
                return '[REDACTED-HIGH-ENTROPY]'
            return s
        
        text = re.sub(r'\b[a-zA-Z0-9+/=]{40,}\b', replace_random, text)
    
    return text

def process_file(filepath, inplace=False, backup=True, aggressive=False):
    """Process a single file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: {filepath} not found", file=sys.stderr)
        return False
    
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False
    
    sanitized = sanitize_text(content, aggressive=aggressive)
    
    if inplace:
        if backup:
            backup_path = str(path) + '.bak'
            shutil.copy2(path, backup_path)
            print(f"Backup created: {backup_path}", file=sys.stderr)
        
        path.write_text(sanitized, encoding='utf-8')
        print(f"Sanitized: {filepath}", file=sys.stderr)
    else:
        print(sanitized, end='')
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Sanitize API keys and secrets from text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.txt                    # Print to stdout
  %(prog)s -i file.txt                 # Edit in-place (with .bak backup)
  %(prog)s -i --no-backup file.txt     # Edit in-place, no backup
  cat log.txt | %(prog)s               # Pipe through stdin
  %(prog)s --aggressive file.txt       # Catch generic high-entropy strings
        """
    )
    parser.add_argument('files', nargs='*', help='Files to process (stdin if empty)')
    parser.add_argument('-i', '--in-place', action='store_true', 
                       help='Edit files in place')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip backup when using -i (DANGEROUS)')
    parser.add_argument('--aggressive', action='store_true',
                       help='Also remove generic high-entropy strings (may have false positives)')
    parser.add_argument('-c', '--check', action='store_true',
                       help='Only check if keys found, exit 1 if found (CI mode)')
    
    args = parser.parse_args()
    
    # Check mode
    if args.check:
        found = False
        sources = args.files if args.files else ['-']
        for src in sources:
            if src == '-':
                content = sys.stdin.read()
            else:
                content = Path(src).read_text(encoding='utf-8', errors='ignore')
            
            sanitized = sanitize_text(content, args.aggressive)
            if content != sanitized:
                found = True
                print(f"Found potential secrets in {src if src != '-' else 'stdin'}", file=sys.stderr)
        sys.exit(1 if found else 0)
    
    # Process files or stdin
    if not args.files:
        # Stdin mode
        content = sys.stdin.read()
        print(sanitize_text(content, args.aggressive), end='')
    else:
        # File mode
        backup = not args.no_backup
        success = True
        for f in args.files:
            if not process_file(f, args.in_place, backup, args.aggressive):
                success = False
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
