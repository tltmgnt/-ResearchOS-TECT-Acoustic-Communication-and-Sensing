import copy
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from researchos_acoustics.records import read_json
from researchos_acoustics.model import analyze
ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('node'),'Node required for web parity')
class WebParityTests(unittest.TestCase):
    def test_full_results_match_python(self):
        base=read_json(ROOT/'examples/synthetic-acoustic.json');cases=[base]
        for seed,delay in [(0,0),(4294967295,256)]:
            r=copy.deepcopy(base);r['seed']=seed;r['ranging']['injected_delay_samples']=delay;cases.append(r)
        script="import fs from 'node:fs';import{analyze}from './web/model.mjs';console.log(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(analyze)))"
        web=json.loads(subprocess.check_output(['node','--input-type=module','-e',script],input=json.dumps(cases),text=True,cwd=ROOT))
        def compare(a,b):
            if isinstance(b,dict):
                self.assertEqual(a.keys(),b.keys())
                for k in b:compare(a[k],b[k])
            elif isinstance(b,list):
                self.assertEqual(len(a),len(b))
                for x,y in zip(a,b):compare(x,y)
            elif type(b) is float:self.assertAlmostEqual(a,b,places=11)
            else:self.assertEqual(a,b)
        for r,result in zip(cases,web):
            with self.subTest(seed=r['seed']):compare(result,analyze(r))
