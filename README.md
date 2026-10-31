# BR-A · 홍지민 공개 포트폴리오와 기록 갱신 장치

**결과물:** https://br-a-portfolio-lime.vercel.app/  
**소스:** https://github.com/jennajiminkim/br-a-portfolio

현재 공식 홈페이지는 저장소 최상위의 **`index.html` 하나**입니다. 사이트 숫자와 사람이 승인한 문단은 `site/site-data.json`을 사용하며, 문서 및 논문은 `site/docs/`에 있습니다. 방문자 로그인·AI 서비스 키는 필요 없습니다. 이전에 사용하던 `site/index.html` 및 `create_site.py`는 구조 혼동과 디자인 덮어쓰기를 막기 위해 정리했습니다.

## README대로 실행하는 3단계

1. `input/` 폴더에 `ritual.json`, `attendance.json`, `submissions.json`, `approvals.json`을 넣습니다. 공개 예시에는 원문 리추얼 대신 날짜별 작성 여부·자기평가·필드 해시만 포함되어 있습니다. **사적인 일지 원문과 동료 실명은 공개하지 않습니다.**
2. 프로젝트 최상위 폴더에서 `python run.py` 또는 `python3 run.py`를 실행합니다. `output/metrics.json`, `output/candidates.json`, `output/review.md`, `output/manifest.json`, `site/site-data.json`이 새로 계산됩니다.
3. `python run.py --list`로 날짜·근거가 붙은 능력별 문단 후보를 읽고, 직접 선택한 항목만 `python run.py --approve cand-... --confirm`으로 승인합니다. 승인 결과만 기존 사이트의 **내 이야기**에 반영됩니다. 승인 전에는 빈 섹션이 보이지 않습니다.

**로컬 미리보기:** 저장소 루트에서 `python -m http.server 8000` 실행 후 `http://localhost:8000/`. 새 기록으로 공개 사이트를 갱신하려면 `site/site-data.json` 변경 사항을 GitHub `main`에 커밋·푸시해야 Vercel 재배포가 됩니다. 로컬 실행만으로 원격 배포되지 않습니다.

## 기록 수치와 출처

- **내 출석 기록:** `input/attendance.json` · 2026-10-30 조회 기준 53/54 출석, 98.1%, 당시 당일 확정 전.
- **리추얼 기록:** `input/ritual.json` · 2026-10-29까지 아침 53일·저녁 52일, 저녁 '일부 실천했다' 22일. `ritual-history-2026-10-29.json` 원본에서 최소 정보만 추린 데이터입니다.
- **내 제출 현황:** `input/submissions.json` · ALEPH 메모리얼 파크 > 내 기록의 공식 화면에서 확인한 마스터 승인 11/13. 전체 과제 목록을 직접 재합산한 값이 아닙니다.
- 9월 22일 SQL 삽입 실습 사례는 그날의 저녁 자기평가와 연결했습니다. 22일 전체가 동일한 어려움을 뜻하지 않습니다.

## 대표작과 서류

- **10번 논문:** `site/docs/manuscript.pdf` (33쪽); 학술 참고문헌 연구자 실명은 사용자가 허용한 예외.
- **13번 비치료적 명상 보조 앱:** 결과물은 아직 없으며 **2026-11-01 예정** 자리만 마련.
- **이력서·자기소개서·경력기술서:** `site/docs/Hong_Jimin_BR-A_Resume.docx`, `site/docs/Hong_Jimin_BR-A_Personal_Statement.docx`, `site/docs/Hong_Jimin_BR-A_Project_Experience.docx`.
- 지원용 이메일 `jenna127001@gmail.com`은 사용자가 직접 선택한 공개 연락처입니다. 사이트 첫 화면과 이력서 DOCX에 동일하게 반영했습니다. 새 시크릿 창 공개 접근은 마지막에 확인합니다.

## 검사 및 제출

- `python tests/check.py`: 동일 입력 두 번, 새 임시 폴더, 날짜 추가, 승인, 근거 변경 시 승인 취소 검사. `tests/reproducibility_result.json`에 저장.
- `python tests/privacy_check.py`: 원본 리추얼 포함 여부와 텍스트·DOCX의 대표적인 연락처·비밀값 패턴 검사. `tests/privacy_result.json`에 저장. 학술 논문 저자 이름은 예외지만 타인 실명에 대한 육안 확인은 필요.
- `submission.md`: 위치·3단계 행동·통과/오류 확인법 및 AI와 본인 판단 세 줄.

**최종 사용자 확인:** 시크릿 창에서 사이트·10번 논문 PDF·문서 3종이 로그인/캡차 없이 열리는지 확인한 뒤, 과제 시스템에 HTTPS 주소 **한 개**와 문서 3종·장치 ZIP을 제출합니다.
