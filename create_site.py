"""One-time creation of the public site frame from the user-approved statement.
Only date/count/approved paragraphs are refreshed by run.py.
"""
from docx import Document
from html import escape
from pathlib import Path
import shutil
root=Path('/mnt/data/BR-A_Updater')
doc=Document('/mnt/data/Hong_Jimin_BR-A_Personal_Statement.docx')
sections=[]; current=None
for p in doc.paragraphs:
    t=p.text.strip()
    if not t or t.startswith('홍지민  |  ') or t.startswith('정보보안 ·'): continue
    if t[:2] in ('01','02','03','04') and t[2:4]=='. ':
        current={'title':t,'paragraphs':[]};sections.append(current)
    elif current:current['paragraphs'].append(t)
markup=[]
for s in sections:
    markup.append('<section class="story-section">')
    markup.append('<h3>'+escape(s['title'])+'</h3>')
    for p in s['paragraphs']:
        cl=' class="quote"' if p.startswith('“') else ''
        markup.append('<p'+cl+'>'+escape(p)+'</p>')
    markup.append('</section>')
story='\n'.join(markup)
html=r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="홍지민의 정보보안 학습·실습 기록과 자기소개">
<title>홍지민 | 정보보안 포트폴리오</title>
<style>
:root{color-scheme:light;--ink:#1e2c3b;--muted:#536879;--line:#dce4eb;--blue:#276bd4;--wash:#f7fafd}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fff;color:var(--ink);font-family:system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;font-size:16px;line-height:1.85}
a{color:var(--blue);text-underline-offset:3px}.wrap{width:min(880px,calc(100% - 44px));margin:auto}header{border-bottom:1px solid var(--line);padding:14px 0;background:white}header .wrap{display:flex;align-items:center;justify-content:space-between;gap:18px}nav{display:flex;gap:16px;flex-wrap:wrap}nav a{font-size:13px;color:var(--muted);text-decoration:none}nav a:hover{text-decoration:underline}.logo{font-weight:700;white-space:nowrap}
.hero{padding:70px 0 55px}.eyebrow{letter-spacing:.15em;text-transform:uppercase;color:var(--blue);font-size:12px;font-weight:700}.hero h1{font-size:clamp(36px,6vw,56px);margin:8px 0;line-height:1.25}.hero p{font-size:clamp(18px,2.9vw,24px);font-weight:550;max-width:720px;line-height:1.6;margin:16px 0 24px}
h2{font-size:26px;line-height:1.4;margin:0 0 22px}h3{font-size:18px;line-height:1.6;margin:0 0 10px}main section.main{padding:42px 0;border-top:1px solid var(--line)}.story-section{margin:0 0 35px}.story-section p{margin:12px 0}.quote{font-size:14px;color:var(--muted);font-style:italic}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.card{border:1px solid var(--line);border-radius:10px;padding:18px}.card strong{font-size:30px;line-height:1.2;display:block;margin-bottom:5px}.card small{color:var(--muted);font-size:12px;display:block;line-height:1.55}.card span{display:block;font-size:14px}.card a{font-size:14px}.projects{display:grid;gap:13px}.subtle{color:var(--muted);font-size:14px}.evidence{font-size:12px;color:var(--muted)}.pill{display:inline-block;border:1px solid var(--line);border-radius:100px;padding:1px 10px;font-size:12px;color:var(--muted)}.empty{padding:18px;border:1px dashed var(--line);color:var(--muted);font-size:14px;border-radius:10px}footer{padding:32px 0 52px;color:var(--muted);font-size:13px;border-top:1px solid var(--line)}:focus-visible{outline:3px solid var(--blue);outline-offset:4px}
@media(max-width:650px){header .wrap{align-items:flex-start;flex-direction:column}nav{gap:12px}.cards{grid-template-columns:1fr}.hero{padding:46px 0}}
</style>
</head>
<body>
<header><div class="wrap"><span class="logo">홍지민</span><nav aria-label="목차"><a href="#story">내 이야기</a><a href="#numbers">기록과 숫자</a><a href="#projects">대표작</a><a href="#approved">내가 승인한 문단</a><a href="#docs">문서</a></nav></div></header>
<main class="wrap">
<div class="hero"><div class="eyebrow">Information Security · Portfolio</div><h1>홍지민</h1><p>대화는 편안하게, 문제는 깊이 있게, 해답은 함께 넓혀가는 사람</p><a href="https://github.com/jennajiminkim" rel="noopener noreferrer" target="_blank">GitHub에서 작업 기록 보기</a></div>
<section id="story" class="main"><h2>내 이야기</h2>__STORY__</section>
<section id="numbers" class="main"><h2>기록과 숫자</h2><div class="cards" id="stats"><div class="empty">숫자 파일을 읽는 중입니다.</div></div><p class="subtle">출석·과제는 학습 사이트의 공식 화면에서 옮겨 적은 값이고, 리추얼 수치는 개인 기록 파일에서 계산합니다. 조회 시점이 서로 다를 수 있습니다.</p><div id="obstacle"></div></section>
<section id="projects" class="main"><h2>대표작</h2><div class="projects">
<div class="card"><h3>10번 과제 · 첫 논문</h3><p>성인 범불안장애 치료 전후 뇌 기능적 연결성 변화 — 공개 출판자료의 근거 종합과 요약통계 재분석</p><p class="subtle">논문 PDF 공개 연결은 최종 개인정보 점검 후 추가합니다.</p></div>
<div class="card"><h3>13번 과제 · 명상 보조 웹 앱</h3><p>비치료적 명상 보조 도구 제작 예정</p><p class="subtle">예상 완료일: 미정 (작성자가 확정 후 입력)</p></div>
</div></section>
<section id="approved" class="main"><h2>승인한 기록 문단</h2><div id="published" class="projects"><div class="empty">승인한 신규 문단이 없습니다.</div></div></section>
<section id="docs" class="main"><h2>문서</h2><p>문서의 상세 내용은 별도 제출물로 제공하며, 아래 파일도 내려받을 수 있습니다.</p><p><a href="docs/Hong_Jimin_BR-A_Resume.docx">이력서 (DOCX)</a> · <a href="docs/Hong_Jimin_BR-A_Personal_Statement.docx">자기소개서 (DOCX)</a> · <a href="docs/Hong_Jimin_BR-A_Project_Experience.docx">경력기술서 (DOCX)</a></p></section>
</main><footer><div class="wrap">홍지민 · 기술 학습과 협업 경험에 관한 공개 포트폴리오</div></footer>
<script>
'use strict';
const $=id=>document.getElementById(id);
function textEl(tag,value,cls){const e=document.createElement(tag);e.textContent=value;if(cls)e.className=cls;return e;}
function stat(parent,value,label,source){const x=textEl('div','','card');x.append(textEl('strong',value),textEl('span',label),textEl('small',source));parent.append(x);}
fetch('./site-data.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('데이터 파일 없음');return r.json()}).then(d=>{
 const m=d.metrics,a=m.attendance,s=m.submissions,r=m.ritual;
 const stats=$('stats');stats.replaceChildren();
 stat(stats,a.percent.toFixed(1)+'%','출석률'+(a.provisional?' · 집계 확정 전':''),a.source);
 stat(stats,s.approved+'/'+s.total+'개','과제 마스터 승인',s.source);
 stat(stats,r.morning_days+'일','아침 기록',r.source+' · '+r.period_start+'~'+r.period_end);
 stat(stats,r.evening_days+'일','저녁 기록 · 일부 실천 '+r.partial_days+'일',r.source+' · 연속 기록일이나 출석일을 뜻하지 않음');
 const o=$('obstacle');o.replaceChildren();
 const block=textEl('div','','card');block.append(textEl('h3','어려움과 숫자를 함께 기록하기'),textEl('p','9월 22일 SQL 삽입 공격 실습에서 여러 번 막혀 도움을 구했습니다. 당시 저녁 기록에는 ‘일부 실천했다’고 남겼습니다. 해당 원본의 저녁 기록 '+r.evening_days+'일 가운데 '+r.partial_days+'일이 같은 평가입니다.'),textEl('small','출처: 2026-09-22 리추얼 저녁 기록 · '+r.source));o.append(block);
 const items=$('published');items.replaceChildren();
 if(!d.approved_paragraphs.length){items.append(textEl('div','신규 후보 중 사용자가 승인한 문단은 아직 없습니다.','empty'));}
 for(const c of d.approved_paragraphs){const el=textEl('article','','card');el.append(textEl('span',c.competency+' · '+c.date,'pill'),textEl('p',c.paragraph),textEl('small','근거: '+c.evidence.date+' · 개인 리추얼 '+c.evidence.field,'evidence'));items.append(el);}
}).catch(e=>{$('stats').replaceChildren(textEl('div','데이터를 불러오지 못했습니다. README의 미리보기 실행 방법을 확인하세요.','empty'));});
</script>
</body></html>
'''.replace('__STORY__',story)
(root/'site/index.html').write_text(html,'utf-8')
for f in ('Resume','Personal_Statement','Project_Experience'):
 src=Path('/mnt/data')/('Hong_Jimin_BR-A_'+f+'.docx')
 shutil.copy2(src,root/'site/docs'/src.name)
print('html generated, user-approved 4 part story; 3 docs copied')
