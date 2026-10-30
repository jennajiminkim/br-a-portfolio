
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
