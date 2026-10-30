# BR-A · 기록으로 다시 쓰는 포트폴리오

Python 표준 라이브러리만 사용하는 **오프라인·결정적(deterministic) 갱신 장치**입니다. AI 호출, 네트워크 요청, API 키가 필요하지 않습니다. 한 번 실행하면 수치를 다시 집계하고 날짜/증거가 붙은 문단 후보를 만들며, **사람이 승인한 후보만** `site/site-data.json`에 실립니다.

## 3단계 실행 (Windows PowerShell / macOS 터미널)

1. 이 폴더의 `input/`에 `ritual.json`, `attendance.json`, `submissions.json`, `approvals.json`을 준비합니다. 포함된 파일은 2026-10-30 조회 기준 안전하게 최소화한 예시입니다.
2. 이 폴더에서 `python run.py`를 실행합니다. 시스템에 따라 `python3 run.py`를 사용합니다. 결과는 `output/metrics.json`, `output/candidates.json`, `output/manifest.json`, `site/site-data.json`에 저장됩니다.
3. `python run.py --list`로 후보의 날짜·내용을 검토합니다. **승인할 문단을 결정한 경우에만** `python run.py --approve cand-... --confirm`을 실행합니다. `site/site-data.json`에는 검증된 승인 문단만 반영됩니다.

### 사이트 확인

`python -m http.server 8000 --directory site` 명령 뒤 브라우저에서 `http://localhost:8000/` 접속 (또는 `python3 -m http.server ...`). 이는 **로컬 미리보기**이며 공개 HTTPS 배포 주소가 아닙니다.

실제 공개 사이트를 갱신하려면 변경된 `site/site-data.json`을 **기존 공개 사이트와 같은 경로에 반영하고 배포해야** 합니다. Git 연동 자동 배포를 설정하면 커밋/푸시가 이 단계를 대신할 수 있습니다. 로컬 명령만으로 원격 사이트가 자동으로 바뀌지는 않습니다. GitHub 저장소 `jennajiminkim/br-a-portfolio`에 소스와 정적 사이트가 등록되어 있습니다. 공개 HTTPS 배포는 별도로 설정해야 합니다.

## 2026-10-30 예시 데이터의 출처

| 파일 | 뜻 | 근거 |
|---|---|---|
| `input/ritual.json` | 원본 개인 리추얼 53개 날짜의 작성여부/자기평가/증거 필드 해시만 포함 | 개인 `ritual-history-2026-10-29.json`, 2026-08-11~10-29 |
| `input/attendance.json` | 재적 54일, 출석 53일 → 98.1%, **10/30 당일 확정 전** | ALEPH `내 출석 기록`, 2026-10-30 화면 수치 수동 전사 |
| `input/submissions.json` | 마스터 승인 11/13, 방어전 도달 22/22 (마무리 자료 전) | ALEPH `메모리얼 파크 > 내 기록`, 2026-10-30 화면 수치 수동 전사 |
| `input/approvals.json` | 본인이 직접 승인한 후보의 ID와 내용 해시 | 처음에는 승인 0건 |

**주의:** 리추얼 공식 화면의 `아침·마무리 모두 쓴 날 53일`과 원본 JSON의 저녁 기록 **52일**은 서로 다릅니다. 출처별 기준을 바꾸거나 합치지 않았습니다. 출석률 98.1%는 `53 / 54 × 100`의 소수 첫째 자리 반올림입니다. 출석과 과제 값은 공식 서비스에 접속해서 가져온 것이 아니라 사용자가 제공한 화면에서 전사한 **스냅샷**입니다. 새로운 공식 화면을 확인할 때 사람이 파일 수치를 갱신해야 합니다.

## 새 기록을 넣는 방법

- **리추얼:** `input/ritual.json`은 공개 가능한 최소화 형태(`format: minimal-ritual-v1`) 또는 비공개 ALEPH 내보내기 형식(`days[].date/open/close`)을 읽습니다. 새 날짜를 추가하면 다음 실행에서 아침/저녁 일수와 후보가 업데이트됩니다. 원본 내보내기 파일을 이 폴더에 넣어 실행했다면 **그 원본을 GitHub, 공개 사이트, 제출 ZIP에 그대로 업로드하지 마세요.** `run.py`는 원문을 결과로 내보내지 않지만 입력 원본을 자동으로 지워 주지도 않습니다.
- **출석:** ALEPH 화면을 다시 확인한 뒤 `input/attendance.json`에서 `snapshot_date`, `enrolled_days`, `attended_days`, `absent_days`, `provisional`을 수정합니다. 데이터 출처도 수정합니다.
- **과제:** `input/submissions.json`의 `approved_snapshot`, `total_snapshot`, `snapshot_date`를 수정합니다. 전체 과제별 목록을 확보하면 `tasks`를 전부 채우고 `task_list_complete:true`로 바꾸세요. 일부 목록만 있는 경우 승인 개수를 목록에서 추정하지 않습니다.
- **후보:** 과거 날짜의 근거가 바뀌면 ID가 달라져 이전 승인 문단은 자동으로 빠지고 다시 승인받습니다. 승인 없이 신규 문단을 자동 게시하지 않습니다.

## 결정적인 결과와 재현성

`python tests/check.py`를 실행하면 다음을 검사합니다.

- 같은 파일로 두 번 실행하여 결과 다섯 파일의 **SHA-256이 동일**한지 확인합니다.
- 새 임시 폴더에 장치를 복사해 README 2단계 명령과 동일한 `python run.py`를 실행하고 같은 파일을 생성하는지 확인합니다.
- 새 기록을 추가해도 집계가 갱신되고 신규 문단이 자동 승인되지 않는지 확인합니다.
- 사람의 승인과 무효화가 의도대로 작동하는지 검증합니다.

결과 요약: `tests/reproducibility_result.json` (테스트 실행 후 생성). 동일 입력 재현을 위해 결과 JSON에 현재 시각, 랜덤값, 머신별 절대경로를 넣지 않습니다.

## 폴더 구성

```text
BR-A_Updater/
  run.py                    # 집계·후보·승인 규칙
  input/
    ritual.json             # 최소화한 날짜/평가/증거 해시 (원문 없음)
    attendance.json         # 출석 스냅샷
    submissions.json        # 과제 목록(부분)과 공식 집계 스냅샷
    approvals.json          # 사용자 승인 목록 (기본 비어 있음)
  output/
    metrics.json            # 출처·기준일이 붙은 숫자
    candidates.json         # 날짜·근거가 붙은 비공개 검토 후보
    review.md               # 검토하기 쉬운 추천 후보 11개
    manifest.json           # 결정성/입력 파일 지문
  site/
    index.html              # 로컬 공개 사이트 원형
    site-data.json          # 숫자 및 승인된 문단만
    docs/                   # 이력서·자기소개서·경력기술서
  tests/
    check.py                # 2회 실행·깨끗한 폴더 시험
    reproducibility_result.json
  submission.md             # 확인 방법 4줄, AI/본인 판단 3줄
```

## 보안 및 게시 유의사항

- **개인적인 리추얼 원문·타인 실명·연락처를 공개하지 마세요.** 제공한 예시는 근거 필드 SHA-256만 포함합니다. `site/site-data.json`에는 원문과 미승인 후보가 들어가지 않습니다.
- 민감정보/API 키/토큰이 필요한 장치가 **아닙니다**. 온라인 AI를 도입할 경우에도 비밀값은 환경 변수로 읽고 `.env`를 업로드하지 마세요.
- `site/`와 문서 3종은 비밀번호 없이 열리는 구조입니다. **원격 HTTPS URL / 시크릿 창 검사는 실제 배포 후 직접 해야 합니다.** 미배포 상태를 통과로 표시하지 않습니다.
- 사용자 이력서의 `[지원용 이메일 주소]`는 아직 임시 문구입니다. 공개 전 사용자가 승인한 연락처로 변경하거나 연락 수단을 GitHub 링크로만 제공하세요.
- 논문 원본 PDF에는 학술 참고문헌의 다른 연구자 실명이 있습니다. **BRA-C10을 문자 그대로 적용하면 재검토가 필요**하므로 공개용 사이트 예시에 PDF를 자동 포함하지 않았습니다. 학술 참고문헌 인용을 허용하는지 확인하고 연결하세요.
- 과제 13 앱의 예상 완료일은 아직 결정되지 않았습니다. 공개 전 사용자 일정으로 수정하세요.

## 재현 실패 시

`python --version`으로 3.9 이상인지 확인하세요. 에러 메시지는 입력 JSON의 형식, 중복 날짜, 출석/승인 숫자 오류, 필수 파일 누락을 알려줍니다. 변경하고 다시 실행하면 됩니다. `pip install`은 필요하지 않습니다.
