"""Reproduce the coordinator's fixed independent full-table protocol.

This protocol is archived after the experiment. A later learning run must
use a fresh independent test protocol rather than train against this one.
"""
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
SNAPSHOT=HERE/'wt-polarization-review'
if not SNAPSHOT.exists():
    SNAPSHOT=HERE.parent/'gaussian'
sys.path.insert(0,str(SNAPSHOT))
import evaluate_dev

if __name__=='__main__':
    result=evaluate_dev.evaluate(seed=84702961,sizes=range(1,9),cases=7,prime=786433)
    assert result['numeric_full_table_checks']==56
    assert result['formal_full_table_checks']==8
    assert result['score']==3670
    print(json.dumps(result,indent=2))
