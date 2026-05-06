# 튜토리얼: Paper Builder 사용법

이 문서는 `paper-builder`를 `manuscript-harness-kit` 위에 얹는 **논문 제작 오케스트레이션 레이어**로 사용하는 방법을 설명합니다.

## 1. 이 레포는 무엇을 하나

이 레포는 하네스를 대체하는 것이 아니라, 그 위에서 다음을 정리해 줍니다.

- 주제, 데이터, 저널 정보를 한 번에 설정
- 워크스페이스 자동 생성
- 하네스 clone 또는 연결
- 하네스용 프로젝트 설정 파일 자동 생성
- 단계별 런북 생성
- 최종 저자 핸드오프 폴더 조립

즉, **코어는 하네스**,  
**진행과 조립은 paper-builder**가 맡는 구조입니다.

## 2. 의존성 설치

```bash
python3 -m pip install -r requirements.txt
```

## 3. 엔진 설정 파일 수정

기본 시작점:

- `config/engine.example.yaml`

먼저 수정할 항목:

- `project.slug`
- `project.title`
- `project.topic`
- `project.study_question`
- `data.primary_dataset`
- `data.dictionary`
- `data.metadata`
- `journal.target_name`
- `harness.mode`

## 4. 워크스페이스 만들기

```bash
python3 scripts/bootstrap_workspace.py config/engine.example.yaml
```

이 명령은 아래 폴더를 만듭니다.

- `workspaces/<slug>/inputs/`
- `workspaces/<slug>/journal/`
- `workspaces/<slug>/generated/`
- `workspaces/<slug>/pipeline/`
- `workspaces/<slug>/handoff/`
- `workspaces/<slug>/logs/`

## 5. 하네스 연결하기

공개 하네스를 `vendor/` 아래로 clone 하려면:

```bash
python3 scripts/clone_harness.py
```

이미 로컬에 하네스가 있으면, 엔진 설정 파일에서 `harness.local_path`를 지정하면 됩니다.

## 6. 저널 인테이크 문서 만들기

```bash
python3 scripts/create_journal_intake.py config/engine.example.yaml
```

현재 이 단계는:

- `journal_intake.md` 생성
- 저널명과 guideline URL 저장
- 이미 알려진 하네스 프로필이 있으면 스냅샷 저장

까지 해줍니다.

아직 하는 것:

- 저널 이름만 넣으면 웹에서 저자 가이드라인을 자동 수집하는 기능은 미구현

## 7. 하네스 프로젝트 생성하기

```bash
python3 scripts/materialize_harness_project.py config/engine.example.yaml
```

이 단계에서:

- 엔진 설정을 하네스용 설정으로 변환
- `generated/project.for_harness.yaml` 저장
- 하네스 `init_project.py` 실행
- 하네스 `run_pipeline.py` 실행

까지 자동으로 진행합니다.

즉 이 단계가 끝나면, 실제 논문작업에 들어갈 하네스 프로젝트가 준비됩니다.

## 8. 사전 점검

```bash
python3 scripts/preflight_check.py config/engine.example.yaml
```

이 스크립트는 다음을 점검합니다.

- Python
- Git
- GitHub CLI 로그인
- 하네스 경로
- Zotero 환경

## 9. 최종 저자 핸드오프

원고와 제출 파일이 정리된 뒤:

```bash
python3 scripts/assemble_author_handoff.py config/engine.example.yaml
```

이 명령은 하네스의 제출 폴더 조립 기능을 감싸서, 저자가 바로 확인할 수 있는 최종 핸드오프 묶음을 만들어 줍니다.

## 10. 현재 한계

- 저널 이름만으로 author guideline 자동 수집은 아직 없음
- 임의 스키마 데이터에 대한 범용 통계엔진은 아직 없음
- Word 안의 live Zotero field 자동 삽입은 아직 없음
- 완전 무인 end-to-end 논문 생성기는 아직 아님

즉 현재 버전은 **실전용 오케스트레이터 v0.1**에 가깝습니다.
