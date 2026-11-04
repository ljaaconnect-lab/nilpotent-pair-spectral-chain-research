"""Run actual pinned Lean feedback; freeze denominator and count every draft run.

No dependencies are installed/built and no shared cache is modified by this
script. It invokes an existing Lean executable with an explicit import path.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT/'rank-one-obligations.json'
STATE = ROOT/'rank-one-progress.json'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True)
    parser.add_argument('--lean-path', required=True)
    parser.add_argument('--environment-json')
    args = parser.parse_args()
    protocol = json.loads(PROTOCOL.read_text(encoding='utf-8'))
    protocol_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    state = (json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else
             {'protocol_sha256': protocol_hash, 'complete_rounds': 0,
              'tactic_probes': 0, 'rounds': []})
    if state['protocol_sha256'] != protocol_hash:
        raise ValueError('The frozen obligations changed')
    if state['complete_rounds'] >= protocol['complete_candidate_budget']:
        raise RuntimeError('Complete candidate budget exhausted')
    source = ROOT/'RankOneSquareZero.lean'
    code = source.read_text(encoding='utf-8')
    stripped = re.sub(r'/-.*?-/|--[^\n]*', '', code, flags=re.S)
    banned = re.findall(r'\b(?:sorry|admit|axiom|unsafe)\b', stripped)
    env = os.environ.copy()
    if args.environment_json:
        inherited = json.loads(Path(args.environment_json).read_text(encoding='utf-8'))
        for key in ('LEAN_SRC_PATH', 'LEAN_SYSROOT'):
            if inherited.get(key):
                env[key] = inherited[key]
    env['LEAN_PATH'] = args.lean_path
    command = [args.lean, str(source)]
    state['complete_rounds'] += 1
    row = {'round': state['complete_rounds'], 'command': command,
           'lean_path': args.lean_path,
           'lean_sysroot': env.get('LEAN_SYSROOT'),
           'timeout_seconds': 180,
           'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
           'banned_tokens': banned}
    if banned:
        row.update(exit_code=None, stdout='', stderr='Rejected placeholder or trust-base extension')
    else:
        try:
            process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=180)
            def decode(raw):
                if raw.count(b'\x00') > len(raw)//5:
                    return raw.decode('utf-16-le', errors='replace').lstrip('\ufeff')
                return raw.decode('utf-8', errors='replace')
            row.update(exit_code=process.returncode,
                       stdout=decode(process.stdout), stderr=decode(process.stderr))
        except (OSError, subprocess.TimeoutExpired) as error:
            row.update(exit_code=None, stdout='', stderr=str(error))
    output = row['stdout']+'\n'+row['stderr']
    axioms = {name: [a.strip() for a in raw.split(',') if a.strip()]
              for name, raw in re.findall(r"'([^']+)'\s+depends on axioms:\s*\[([^\]]*)\]", output)}
    for name in re.findall(r"'([^']+)'\s+does not depend on any axioms", output):
        axioms[name] = []
    approved = set(protocol['trust_base'])
    unapproved = {name: sorted(set(used)-approved)
                  for name, used in axioms.items() if set(used)-approved}
    accepted = ([item['name'] for item in protocol['obligations']
                 if item['name'] in axioms and not (set(axioms[item['name']])-approved)]
                if row['exit_code'] == 0 and not banned and not unapproved else [])
    row['accepted'] = accepted
    row['axiom_audit'] = axioms
    row['unapproved_axioms'] = unapproved
    state['rounds'].append(row)
    state.update(accepted=accepted, dev_score=len(accepted)/protocol['obligation_count'],
                 obligation_count=protocol['obligation_count'],
                 root_conjecture_verified=False)
    STATE.write_text(json.dumps(state, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'round': row['round'], 'exit_code': row['exit_code'],
                      'accepted': accepted, 'dev_score': state['dev_score'],
                      'stdout': row['stdout'], 'stderr': row['stderr']}, indent=2))
    sys.exit(0 if row['exit_code'] == 0 else 1)


if __name__ == '__main__':
    main()
