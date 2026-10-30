#!/usr/bin/env python3
"""BR-A: Deterministic diary/attendance/submission updater (Python 3.9+, stdlib only).

NO AI, network, tokens or API calls. Results contain no raw diary text.
Public candidates only after explicit human approval verified by content hash.
"""
import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

BASE=Path(__file__).resolve().parent
INPUT=BASE/'input'; OUT=BASE/'output'; SITE=BASE/'site'
DIMS=('자기조절력','대인관계력','자기동기력')
TRIGGERS={
 '자기조절력': ('막히','오류','수정','다시','원인','해결','실패','검증','확인'),
 '대인관계력': ('팀원','조원','함께','의견','도움','공유','동료','웹 서버','협업'),
 '자기동기력': ('수업','꾸준','공부','학습','복습','완료','남아서','도전','리눅스'),
}
FIELDS=('강점이 드러난 일화','강점을 위해 노력하고 생각한 것',
        '동료 1가 나눈 감사','동료 2가 나눈 감사','동료 3가 나눈 감사')
# Each explicit case is supported by a private source-field hash; no personal diary text is republished.
CURATED={
 ('2026-08-27','자기동기력'):'정규 보안 수업을 마친 뒤에도 기초 리눅스 수업을 이어가며 부족한 지식을 보완했습니다.',
 ('2026-09-10','대인관계력'):'웹 서버 공동 구축에서 화면 구성을 맡고 PHP 구조 구현에 참여했습니다. 진행 상황을 정리하며 팀원들의 아이디어를 공유했습니다.',
 ('2026-09-22','자기조절력'):'SQL 삽입 실습을 여러 차례 시도했지만 원하는 결과를 얻지 못하자 동료에게 도움을 청하고 문제를 다시 살폈습니다.',
 ('2026-10-07','자기동기력'):'방어전 실습에서 막혔을 때 도움을 구하고 수업 후에도 방법을 찾아 5단계까지 마쳤습니다.',
 ('2026-10-14','자기조절력'):'방어전 8단계에서 막혔지만 수업 후에도 문제를 살펴 해결하고, 실패 원인까지 확인했습니다.',
}
CURATED_FIELD={
 ('2026-08-27','자기동기력'):'.open[',
 ('2026-09-10','대인관계력'):'.close[',
 ('2026-09-22','자기조절력'):'.close[',
 ('2026-10-07','자기동기력'):'.open[',
 ('2026-10-14','자기조절력'):'.open[',
}
GENERIC={
 '자기조절력':'해당 날짜의 일지에 문제를 다시 확인하거나 해결 방법을 조정한 기록이 있습니다. 실제 행동과 결과를 검토해 소개 문장으로 다듬을 후보입니다.',
 '대인관계력':'해당 날짜의 일지에 다른 사람과 의견을 나누거나 서로 도운 기록이 있습니다. 협업 과정과 기여 내용을 검토할 후보입니다.',
 '자기동기력':'해당 날짜의 일지에 학습을 계속하거나 목표를 실행한 기록이 있습니다. 구체적인 행동을 확인해 보완할 후보입니다.',
}

def dump(x): return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
def h(b): return hashlib.sha256(b if isinstance(b,bytes) else b.encode('utf-8')).hexdigest()
def read(name): return json.loads((INPUT/name).read_text('utf-8'))
def require(cond,msg):
 if not cond: raise ValueError(msg)

def normalize_ritual(data):
 """Accept reduced public-safe JSON or a PRIVATE original ALEPH export.
 The private original is NEVER copied into output/site."""
 if data.get('format')=='minimal-ritual-v1':
  days=data['days']
 else:
  require(isinstance(data.get('days'),list),'리추얼 days 배열이 없습니다')
  days=[]
  for d in data['days']:
   ev=[]
   for section in ('open','close'):
    for idx,entry in enumerate(d.get(section) or []):
     if not isinstance(entry,str) or ':' not in entry: continue
     label,value=entry.split(':',1)
     if label not in FIELDS or not value.strip():continue
     for dim,terms in TRIGGERS.items():
      if any(t in value for t in terms):
       ev.append({'competency':dim,'field':f'days[{d["date"]}].{section}[{idx}]','sha256':h(value.strip())})
   evaluation=next((z.split(':',1)[1].strip() for z in (d.get('close') or []) if z.startswith('강점 행동:')),None)
   days.append({'date':d['date'],'morning_present':bool(d.get('open')),'evening_present':bool(d.get('close')),
                'self_assessment':evaluation,'evidence':ev})
 require(len({d['date'] for d in days})==len(days),'중복 날짜가 있습니다')
 for d in days:
  date.fromisoformat(d['date'])
  require(isinstance(d['morning_present'],bool) and isinstance(d['evening_present'],bool),'리추얼 기록 여부 형식 오류')
  if not d['evening_present']:
   require(d['self_assessment'] is None,'저녁 기록 없이 자기평가가 존재합니다: '+d['date'])
  require(d['self_assessment'] in (None,'실천했다','일부 실천했다','실천하지 못했다'), '알 수 없는 자기평가: '+str(d['self_assessment']))
  for e in d.get('evidence',[]):
   require(e['competency'] in DIMS and bool(re.fullmatch(r'[0-9a-f]{64}',e['sha256'])),'증거 항목 오류')
   require(e['field'].startswith('days['+d['date']+']'),'증거 필드 날짜가 일치하지 않습니다')
 return sorted(days,key=lambda x:x['date'])

def counts(days,att,sub,ritual_name):
 morning=sum(d['morning_present'] for d in days)
 evening=sum(d['evening_present'] for d in days)
 done=sum(d['self_assessment']=='실천했다' for d in days)
 partial=sum(d['self_assessment']=='일부 실천했다' for d in days)
 notdone=sum(d['self_assessment']=='실천하지 못했다' for d in days)
 attended=att['attended_days']; enrolled=att['enrolled_days']
 require(isinstance(attended,int) and isinstance(enrolled,int) and 0<=attended<=enrolled and enrolled>0,'출석 숫자가 잘못되었습니다')
 require(0<=att['absent_days']<=enrolled,'결석 숫자가 잘못되었습니다')
 approved=sub['approved_snapshot'];total=sub['total_snapshot']
 require(isinstance(approved,int) and isinstance(total,int) and 0<=approved<=total and total>0,'과제 숫자가 잘못되었습니다')
 tasks=sub.get('tasks',[])
 ids=[t['id'] for t in tasks]
 require(len(ids)==len(set(ids)),'과제 목록 ID 중복')
 if sub.get('task_list_complete'):
  require(len(tasks)==total,'전체 과제 목록의 수가 total_snapshot과 다릅니다')
  require(sum(t['status']=='approved' for t in tasks)==approved,'과제별 승인 개수와 공식 집계 불일치')
 return {
  'attendance':{'percent':round(100*attended/enrolled,1),'attended_days':attended,'enrolled_days':enrolled,
    'absent_days':att['absent_days'],'as_of':att['snapshot_date'],'provisional':bool(att.get('provisional')),
    'source':att['source'],'source_type':att['source_type']},
  'submissions':{'approved':approved,'total':total,'as_of':sub['snapshot_date'],'source':sub['source'],
    'list_complete':bool(sub.get('task_list_complete')),'source_type':sub['source_type'],
    'defense_progress':sub.get('defense_progress')},
  'ritual':{'morning_days':morning,'evening_days':evening,'done_days':done,'partial_days':partial,
    'not_done_days':notdone,'period_start':days[0]['date'] if days else None,
    'period_end':days[-1]['date'] if days else None,'source':ritual_name,
    'source_type':'derived_from_original_private_export_minimized' if ritual_name=='ritual-history-2026-10-29.json' else 'user_provided_ritual_export',
    'note':'리추얼 일수는 출석일이나 연속 작성일과 다릅니다.'},
 }

def candidates(days,source_label):
 result=[]
 for d in days:
  bydim=defaultdict(list)
  for e in d.get('evidence',[]): bydim[e['competency']].append(e)
  for dim in DIMS:
   if not bydim[dim]:continue
   choices=sorted(bydim[dim],key=lambda a:(a['field'],a['sha256']))
   preferred=CURATED_FIELD.get((d['date'],dim))
   ev=next((x for x in choices if preferred and preferred in x['field']), choices[0])
   is_curated=(d['date'],dim) in CURATED
   sentence=CURATED[(d['date'],dim)] if is_curated else GENERIC[dim]
   # For generic candidates, date is presented separately; no raw text published.
   digest=h(sentence)
   identifier='cand-'+h('|'.join([d['date'],dim,ev['field'],ev['sha256'],digest]))[:14]
   result.append({'id':identifier,'date':d['date'],'competency':dim,'type':'날짜 기반 검토 후보',
    'paragraph':sentence,'content_sha256':digest,
    'evidence':{'source':source_label,'date':d['date'],'field':ev['field'],'evidence_sha256':ev['sha256']},
    'requires_approval':True,'note':'원문을 게시하지 않습니다. 내용과 다른 사람의 정보가 없는지 직접 검토 후 승인하세요.'})
 return sorted(result,key=lambda x:(x['date'],DIMS.index(x['competency']),x['id']))

def run(args):
 ritual=read('ritual.json');att=read('attendance.json');sub=read('submissions.json');appr=read('approvals.json')
 days=normalize_ritual(ritual)
 source_label=ritual.get('source_basename') if ritual.get('format')=='minimal-ritual-v1' else 'ritual.json (비공개 원본)'
 all_candidates=candidates(days,source_label)
 lookup={v['id']:v for v in all_candidates}
 if args.approve:
  require(args.confirm,'승인할 때는 후보 내용 확인 후 --confirm을 함께 입력하세요.')
  require(args.approve in lookup,'승인 후보 ID가 없습니다: '+args.approve)
  v=lookup[args.approve]
  entry={'id':v['id'],'content_sha256':v['content_sha256']}
  approved=appr.setdefault('approved',[])
  if entry not in approved: approved.append(entry)
  approved.sort(key=lambda x:x['id'])
  (INPUT/'approvals.json').write_bytes(dump(appr))
 approved=[]; stale=[]
 for entry in appr.get('approved',[]):
  v=lookup.get(entry['id'])
  if v and v['content_sha256']==entry.get('content_sha256'):
   approved.append(v)
  else: stale.append(entry['id'])
 metric=counts(days,att,sub,source_label)
 review={'competencies':list(DIMS),'candidate_count':len(all_candidates),'candidates':all_candidates,
  'approved_count':len(approved),'stale_approvals':sorted(stale),
  'review_instructions':'검토 후 python run.py --approve 후보ID --confirm을 실행하세요. 자동 승인은 하지 않습니다.'}
 public={'schema_version':1,'name':'홍지민','headline':'대화는 편안하게, 문제는 깊이 있게, 해답은 함께 넓혀가는 사람',
  'metrics':metric,'approved_paragraphs':[{k:v[k] for k in ('id','date','competency','paragraph','evidence')} for v in approved],
  'approval_policy':'문단은 사용자가 승인한 항목만 공개합니다. 수치는 입력 자료를 다시 집계합니다.'}
 inputs={p.name:h(p.read_bytes()) for p in sorted(INPUT.glob('*.json'))}
 manifest={'input_sha256':inputs,'metric_sha256':h(dump(metric)),'candidates_sha256':h(dump(review)),
  'site_data_sha256':h(dump(public)),'approved_count':len(approved),
  'notes':['로컬 파일과 내장 규칙만 사용','시각/랜덤값/AI API 사용하지 않음','원문 기록은 출력하지 않음']}
 files={OUT/'metrics.json':metric,OUT/'candidates.json':review,SITE/'site-data.json':public,OUT/'manifest.json':manifest}
 OUT.mkdir(exist_ok=True);SITE.mkdir(exist_ok=True)
 for path,value in files.items():path.write_bytes(dump(value))
 picks=[x for x in all_candidates if (x['date'],x['competency']) in CURATED]
 for dim in DIMS:
  recent=sorted((x for x in all_candidates if x['competency']==dim and x not in picks),key=lambda x:x['date'],reverse=True)[:2]
  picks.extend(recent)
 review_lines=['# BR-A · 검토 추천 후보','', '모든 문단은 **미승인 상태**로 시작합니다. 아래 내용과 근거 날짜를 읽고 본인이 승인할 때만 게시됩니다.','']
 for v in sorted(picks,key=lambda x:(x['competency'],x['date'])):
  review_lines.extend([f'## {v["competency"]} · {v["date"]}',v['paragraph'],'',f'근거: {v["evidence"]["source"]} / {v["evidence"]["field"]}',f'승인 명령: `python run.py --approve {v["id"]} --confirm`',''])
 (OUT/'review.md').write_text('\n'.join(review_lines)+'\n','utf-8')
 print('완료:',f'아침 {metric["ritual"]["morning_days"]}일 / 저녁 {metric["ritual"]["evening_days"]}일',
 f'출석 {metric["attendance"]["percent"]}% / 과제 {metric["submissions"]["approved"]}/{metric["submissions"]["total"]}')
 print('문단 후보',len(all_candidates),'개 / 사용자 승인 후 공개',len(approved),'개 / 유효하지 않은 과거 승인',len(stale),'개')
 if args.list:
  for v in all_candidates:print(v['id'],v['date'],v['competency'],v['paragraph'])
 return files

def cli():
 p=argparse.ArgumentParser(description='BR-A 기록 업데이트 장치')
 p.add_argument('--list',action='store_true',help='후보 날짜·문단 목록 표시')
 p.add_argument('--approve',metavar='ID',help='사람이 직접 검토한 후보 ID 승인')
 p.add_argument('--confirm',action='store_true',help='게시 승인 의사를 명시적으로 확인')
 args=p.parse_args()
 try:run(args)
 except (ValueError,KeyError,TypeError,FileNotFoundError,json.JSONDecodeError) as e:
  print('오류:',e,file=sys.stderr);sys.exit(2)

if __name__=='__main__':cli()
