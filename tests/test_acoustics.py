import copy
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from researchos_acoustics.model import RNG, analyze, erfc_approx
from researchos_acoustics.records import ValidationError, dumps, read_json, sha, validate
from researchos_acoustics.workflow import run, verify_bundle, verify_evidence
ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/'examples/synthetic-acoustic.json'

class AcousticTests(unittest.TestCase):
    def setUp(self):
        self.r=read_json(EXAMPLE)
    def test_link_equations_and_known_samples(self):
        result=analyze(self.r)
        a,b,c,d=result['link_results']
        self.assertEqual(a['relative_loss_db'],0)
        self.assertAlmostEqual(b['relative_loss_db'],20*math.log10(2))
        self.assertAlmostEqual(d['received_ebn0_db'],18-20*math.log10(8))
        self.assertEqual(d['simulated_bit_errors'],337)
        self.assertGreater(d['approx_theoretical_ber'],c['approx_theoretical_ber'])
        self.assertAlmostEqual(d['one_way_delay_s'],8/343)
    def test_erfc_and_seed_reproduction(self):
        for x in [0,.01,.1,.5,1,2,4,8]:
            self.assertAlmostEqual(erfc_approx(x),math.erfc(x),delta=1e-7)
        self.assertEqual(analyze(self.r),analyze(self.r))
        self.assertEqual(RNG(42).uniform(),(1083814273+.5)/4294967296)
    def test_noiseless_ranging_and_boundary_delays(self):
        self.r['ranging']['noise_std']=0
        for delay in [0,96,256]:
            self.r['ranging']['injected_delay_samples']=delay
            result=analyze(self.r)['ranging_results']
            self.assertEqual(result['estimated_delay_samples'],delay)
            self.assertEqual(result['absolute_range_error_m'],0)
            self.assertAlmostEqual(result['estimated_range_m'],343*delay/96000)
    def test_noise_only_is_not_certified_detection(self):
        self.r['ranging']['echo_gain']=0
        self.assertEqual(analyze(self.r)['ranging_results']['detection_status'],'unthresholded-maximum-only')
    def test_invalid_inputs(self):
        mutations=[lambda r:r.update(schema_version=True),lambda r:r.update(id='../escape'),lambda r:r.update(seed=True),lambda r:r['link'].update(bits=0),lambda r:r['link'].update(distances_m=[.5]),lambda r:r['link'].update(sound_speed_m_s=0),lambda r:r['ranging'].update(injected_delay_samples=257),lambda r:r['ranging'].update(noise_std=-1),lambda r:r.update(data_kind='experimental')]
        for mutate in mutations:
            r=copy.deepcopy(self.r);mutate(r)
            with self.subTest(record=r),self.assertRaises(ValidationError):validate(r)
        self.r['link']['absorption_db_km']=1e6
        with self.assertRaises(ValidationError):analyze(self.r)
    def test_evidence_and_experimental_measurements(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=b'fixture, not real evidence';(root/'raw').write_bytes(data)
            self.r['data_kind']='experimental';self.r['evidence']=[{'id':'raw','path':'raw','sha256':sha(data),'description':'Test only'}]
            self.r['measurements']=[{'metric':'distance','unit':'m','value':1,'uncertainty':.1,'method':'Fixture','evidence_ids':['raw']}]
            p=root/'record.json';p.write_text(dumps(self.r));run(p,root/'run');(root/'raw').unlink();verify_bundle(root/'run')
            (root/'run/evidence/0000.bin').write_bytes(b'changed')
            with self.assertRaises(ValidationError):verify_bundle(root/'run')
    def test_paths_and_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'raw').write_bytes(b'actual');self.r['evidence']=[{'id':'raw','path':'raw','sha256':sha(b'wrong'),'description':'Test'}]
            with self.assertRaises(ValidationError):verify_evidence(validate(self.r),root)
            for path in ['../outside','/etc/passwd','C:\\absolute']:
                self.r['evidence'][0]['path']=path
                with self.assertRaises(ValidationError):validate(self.r)
            (root/'link').symlink_to(root.parent);self.r['evidence'][0]['path']='link/outside'
            with self.assertRaises(ValidationError):verify_evidence(validate(self.r),root)
    def test_bundle_reproduction_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b';run(EXAMPLE,a);run(EXAMPLE,b);verify_bundle(a)
            self.assertEqual({p.relative_to(a):p.read_bytes() for p in a.rglob('*') if p.is_file()},{p.relative_to(b):p.read_bytes() for p in b.rglob('*') if p.is_file()})
            with self.assertRaises(ValidationError):run(EXAMPLE,a)
            result=read_json(a/'results.json');result['link_results'][0]['simulated_ber']=1;(a/'results.json').write_text(dumps(result));manifest=read_json(a/'manifest.json');manifest['files']['results.json']=sha((a/'results.json').read_bytes());(a/'manifest.json').write_text(dumps(manifest))
            with self.assertRaises(ValidationError):verify_bundle(a)
    def test_strict_json_and_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.json'
            for data in ['{"x":1,"x":2}','{"x":NaN}']:
                p.write_text(data)
                with self.assertRaises(ValidationError):read_json(p)
            output=str(Path(tmp)/'run')
            for args in [['validate',str(EXAMPLE)],['run',str(EXAMPLE),'--output',output],['verify',output],['report',output]]:
                r=subprocess.run([sys.executable,'-m','researchos_acoustics',*args],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
