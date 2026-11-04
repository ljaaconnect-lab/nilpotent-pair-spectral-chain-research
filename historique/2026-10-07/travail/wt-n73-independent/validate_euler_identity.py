import argparse
import hashlib
import json
import time
from pathlib import Path
from euler_identity import check_identities


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, required=True)
    args = p.parse_args()
    root = Path(__file__).resolve().parent
    frozen = root / 'n61-protocol.json'
    started = time.perf_counter()
    result = check_identities(args.n)
    result['elapsed_seconds'] = time.perf_counter()-started
    result['protocol_sha256'] = hashlib.sha256(frozen.read_bytes()).hexdigest()
    (root / f'n61-identity-n{args.n}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)
    if not result['euler_diagonal_identity'] or not result['grouped_row_identity']:
        raise SystemExit('Frozen positive identity validation failed')


if __name__ == '__main__':
    main()
