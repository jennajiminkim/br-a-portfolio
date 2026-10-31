#!/usr/bin/env python3
"""Heuristic leakage scan; does not replace a human review of all names/content."""
from pathlib import Path
import json,re,zipfile,xml.etree.ElementTree as ET
base=Path(__file__).resolve().parents[1]
allowed={'.json','.html','.md','.py','.js','.txt','.gitignore'}
patterns={
 'email_address': re.compile(r'(?i)\b[\w.+%-]+@[\w.-]+\.[a-z]{2,}\b'),
 'phone_number': re.compile(r'(?<!\d)(?:\+?82[-\s]?)?01[016789][\s-]?\d{3,4}[\s-]?\d{4}(?!\d)'),
 'key_assignment': re.compile(r'(?im)^\s*(?:api[_-]?key|secret|password|token)\s*[=:]\s*["\']?([A-Za-z0-9_-]{12,})["\']?\s*$'),
 'jwt': re.compile(r'\beyJ[A-Za-z0-9_-]{14,}\.eyJ[A-Za-z0-9_-]{14,}'),
 'aws_secret': re.compile(r'\bAKIA[A-Z0-9]{16}\b'),
}
issue=[];scanned=[]
for f in sorted(base.rglob('*')):
 if not f.is_file() or '__pycache__' in str(f) or f.name.endswith('.pyc'):continue
 if f.suffix=='.pdf':
  rel=str(f.relative_to(base))
  if rel=='site/docs/manuscript.pdf':
   if not f.read_bytes()[:8].startswith(b'%PDF-'):issue.append({'file':rel,'type':'bad_pdf_header'})
  else:issue.append({'file':rel,'type':'unexpected_pdf'})
  continue
 if f.suffix=='.docx':
  with zipfile.ZipFile(f) as z:
   txt=[]
   for n in z.namelist():
    if n.startswith('word/') and n.endswith('.xml'):
     try:
      node=ET.fromstring(z.read(n)); txt.extend((e.text or '') for e in node.iter() if e.tag.endswith('}t'))
     except ET.ParseError:pass
   content=' '.join(txt)
 elif f.suffix in allowed or f.name.startswith('.'):
  content=f.read_text('utf-8')
 else:continue
 scanned.append(str(f.relative_to(base)))
 for label,pattern in patterns.items():
  for mt in pattern.finditer(content):
   issue.append({'file':str(f.relative_to(base)),'type':label,'location':mt.start()})
 # raw diary text would be stored as open/close arrays, not in safe reduced format.
 if f==base/'input/ritual.json':
  ritual=json.loads(content)
  if ritual.get('format')!='minimal-ritual-v1':issue.append({'file':'input/ritual.json','type':'PRIVATE_RAW_DIARY_INPUT'})
result={'automatic_scan':'PASS' if not issue else 'FAIL','files_scanned':len(scanned),'issues':issue,
        'manual_review_note':'이름/인용/서사상 개인 식별 여부는 자동 정규식만으로 확정할 수 없으므로 배포 전 사람의 추가 검토가 필요함.',
        'pdf_status':'site/docs/manuscript.pdf 논문 학술 참고문헌의 저자 이름은 사용자 승인 예외. 논문 원문은 별도 육안 확인 필요'}
(base/'tests/privacy_result.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n','utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if issue:raise SystemExit(1)
