"""
Master runner: executes Stages 1-6 in sequence, halting on first failure.
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

HERE = os.path.dirname(os.path.abspath(__file__))

STAGES = [
    ('Stage 1 — Parameters',      'run_stage1.py'),
    ('Stage 2 — Graph + CK-G*',   'run_stage2.py'),
    ('Stage 3 — Labels + CK-L*',  'run_stage3.py'),
    ('Stage 4 — Hash lock',        'run_stage4.py'),
    ('Stage 5 — Dynamics units',   'run_stage5.py'),
    ('Stage 6 — Acceptance tests', 'run_stage6.py'),
]


def run():
    print('=' * 60)
    print('PHASE 7B: Reference implementation — all stages')
    print('=' * 60)

    all_pass = True
    for stage_name, script in STAGES:
        print(f'\n>>> {stage_name}')
        result = subprocess.run(
            [sys.executable, os.path.join(HERE, script)],
            capture_output=False,
        )
        if result.returncode != 0:
            print(f'\nHALTED: {stage_name} failed (exit code {result.returncode})')
            all_pass = False
            break

    print('\n' + '=' * 60)
    if all_pass:
        print('ALL STAGES PASSED — implementation ready for simulation')
    else:
        print('PHASE 7B INCOMPLETE — fix failures before proceeding')
    print('=' * 60)
    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    run()
