#!/usr/bin/env python3
"""Test in-place twice, a clean-folder copy, future new day, explicit approval, and stale approval."""
from pathlib import Path
import hashlib, json, subprocess, shutil, tempfile, sys
root=Path(__file__).resolve().parents[1]
names=['output/metrics.json','output/candidates.json','output/manifest.json','site/site-data.json','output/review.md']
def check(cmd,dir):
 x=subprocess.run([sys.executable,'run.py',*cmd],cwd=dir,capture_output=True,text=True,encoding='utf-8')
 if x.returncode:raise RuntimeError(f'code={x.returncode}, stderr={x.stderr}, stdout={x.stdout}')
 return x.stdout
def fingerprints(dir):return {n:hashlib.sha256((dir/n).read_bytes()).hexdigest() for n in names}

def main():
 a=check([],root);first=fingerprints(root)
 b=check([],root);second=fingerprints(root)
 assert first==second,'동일 폴더 2회 실행 결과가 다릅니다'
 with tempfile.TemporaryDirectory(prefix='bra-clean-') as t:
  new=Path(t)/'BR-A_Updater'
  shutil.copytree(root,new,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
  c=check([],new); fresh=fingerprints(new)
  assert first==fresh,'새 폴더 실행 결과가 다릅니다'
  # user-approved-only gate
  snap=json.loads((new/'site/site-data.json').read_text('utf-8'))
  assert len(snap['approved_paragraphs'])==0,'승인 전 공개됨'
  cands=json.loads((new/'output/candidates.json').read_text('utf-8'))['candidates']
  chosen=next(x for x in cands if x['date']=='2026-09-10' and x['competency']=='대인관계력')
  check(['--approve',chosen['id'],'--confirm'],new)
  published=json.loads((new/'site/site-data.json').read_text('utf-8'))['approved_paragraphs']
  assert len(published)==1 and published[0]['id']==chosen['id'],'승인 게이트 실패'
  # replace a minimized evidence hash to invalidate previously approved paragraph
  raw=json.loads((new/'input/ritual.json').read_text('utf-8'))
  dd=next(x for x in raw['days'] if x['date']=='2026-09-10')
  for ev in dd['evidence']:
   if ev['competency']=='대인관계력':ev['sha256']='a'*64
  (new/'input/ritual.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n','utf-8')
  check([],new)
  freshdata=json.loads((new/'site/site-data.json').read_text('utf-8'))
  assert len(freshdata['approved_paragraphs'])==0,'과거 근거 변경 시 승인이 취소되지 않음'
  # new day added to minimized diary; no automatic publication
  raw['days'].append({'date':'2026-11-01','morning_present':True,'evening_present':True,
                      'self_assessment':'실천했다',
                      'evidence':[{'competency':'자기동기력','field':'days[2026-11-01].open[0]', 'sha256':'b'*64}]})
  (new/'input/ritual.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n','utf-8')
  check([],new)
  m=json.loads((new/'output/metrics.json').read_text('utf-8'))['ritual']
  assert m['morning_days']==54 and m['evening_days']==53,'신규 기록 집계 실패'
  cands2=json.loads((new/'output/candidates.json').read_text('utf-8'))['candidates']
  assert any(x['date']=='2026-11-01' and x['competency']=='자기동기력' for x in cands2),'신규 날짜 후보 생성 실패'
  assert len(json.loads((new/'site/site-data.json').read_text('utf-8'))['approved_paragraphs'])==0,'신규 후보 자동 공개됨'
 result={'same_input_twice':'PASS' if first==second else 'FAIL', 'clean_folder':'PASS' if first==fresh else 'FAIL',
         'explicit_approval':'PASS','stale_approval_revoked':'PASS','new_records_update_metrics':'PASS',
         'new_records_require_approval':'PASS','fingerprints':first,
         'checked_files':names,'note':'테스트 로그에는 현재 시간과 절대경로가 없어 재현 결과에 영향을 주지 않습니다.'}
 (root/'tests/reproducibility_result.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in result.items() if k not in ('fingerprints','checked_files')},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
