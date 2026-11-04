"""Snapshot real compiler counts; never infer success from a running process."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RUN=ROOT/'research/.arbor/run.json'
run=json.loads(RUN.read_text(encoding='utf-8'))
records=[]
for node in ('n71','n73','n75','n76'):
    directory=ROOT/f'wt-{node}'
    logs=list((directory/f'{node}-compiler-rounds').glob('round-*.json'))
    if node=='n76':logs+=list(directory.glob('n76-round-*-report.json'))
    for f in logs:
        records.append((node,f.name,json.loads(f.read_text(encoding='utf-8'))['exit_code']))
deps=1 if (ROOT/'wt-n75/n75-dependency-build.json').exists() else 0
replays=[f for f in ROOT.glob('n*-independent-replay.json') if f.name in
         ('n73-independent-replay.json','n75-independent-replay.json','n76-independent-replay.json')]
replays+=list(ROOT.glob('n75-independent-replay-attempt-*.json'))
replays+=list(ROOT.glob('n76-independent-replay-attempt-*.json'))
actual=len(records)+deps+len(replays)
assert actual<=20, ('Shared formal cap exceeded',actual)
run['current_formal_window'].update({
    'actual_complete_candidate_compilations':len(records),
    'actual_dependency_compilations':deps,
    'actual_independent_commit_replays':len(replays),
    'actual_total_compiler_invocations':actual,
    'candidate_exit_records':records,
})
RUN.write_text(json.dumps(run,indent=2),encoding='utf-8')
print(json.dumps({'actual_started_invocations':actual,
                  'actual_completed_invocations':sum(code is not None for _,_,code in records)+deps+len(replays),
                  'candidate_records':records}))
