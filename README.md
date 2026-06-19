# TOA AI

TOA AI는 OHLCV 시계열 데이터를 SQLite 메모리에 저장하고, 누수 방지형 피처/라벨을 생성해 정책 모델을 학습한 뒤, paper replay로 의사결정과 주문 게이트를 검증하는 연구용 트레이딩 AI 패키지입니다.

이 저장소는 `auto_trader` 전체 프로젝트가 아니라 `toa_ai` 패키지만 별도로 공개하기 위한 버전입니다. 실거래 자동매매 시스템이 아니라, 모델 학습과 리플레이 검증을 위한 오픈소스 연구 코드로 보는 것이 맞습니다.

> 투자 조언이 아닙니다. 이 프로젝트는 수익을 보장하지 않으며, 기본 설정은 실주문을 내지 않는 연구/모의 환경입니다.

## 주요 기능

- SQLite 기반 TOA Memory
  - 시장 봉 데이터, 모델 의사결정, 주문, 체결, 경험 샘플, 모델 레지스트리 저장
- 외부 OHLCV 데이터 적재
  - 일반 CSV, Binance kline CSV/ZIP, 로컬 캐시 CSV 지원
- 누수 방지 피처 생성
  - 수익률, 캔들 구조, 거래량 z-score, VWAP 거리, RSI, MACD histogram, ATR, realized volatility, 시간 피처 등 28개 기본 피처
- 정책 모델 학습
  - GRU encoder 기반 `TOAPolicyNet`
  - action classification, expected return, risk score를 함께 학습
- 리플레이 검증
  - 과거 봉을 순차적으로 읽으며 정책 출력, 실행 가능 action 선택, risk gate, paper broker 체결을 기록
- Promotion gate
  - validation loss, action entropy, no-action 비율 등 최소 품질 조건을 통과한 challenger만 champion으로 승격
- Smoke workflow
  - 합성 데이터로 DB 초기화, 학습, 승격, 리플레이까지 한 번에 점검

## 현재 모델 구조

TOA AI v1 정책 모델은 다음 형태입니다.

```text
OHLCV bars
  -> feature frame, 28 columns
  -> rolling sequence, default 64 bars
  -> GRU encoder
  -> action head: NO_ACTION / OPEN_LONG / HOLD_LONG / REDUCE_LONG / CLOSE_LONG
  -> expected return head
  -> risk score head
  -> holding score head
  -> risk governor
  -> paper broker / replay logs
```

기본 action class는 다음 5개입니다.

- `NO_ACTION`
- `OPEN_LONG`
- `HOLD_LONG`
- `REDUCE_LONG`
- `CLOSE_LONG`

라벨은 미래 구간을 직접 예측 대상으로 쓰지만, 모델 입력 sequence에는 현재 시점까지 완료된 봉만 들어가도록 구성되어 있습니다. 리플레이도 각 bar 시점마다 과거 데이터만 잘라서 feature를 다시 생성합니다.

## 저장소 구조

공개 저장소는 아래 구조를 기준으로 구성합니다.

```text
toa-ai/
  README.md
  requirements.txt
  .gitignore
  toa_ai/
    __init__.py
    cli.py
    config.py
    domain.py
    features.py
    policy.py
    trainer.py
    replay.py
    risk.py
    storage.py
    ...
```

루트에는 문서와 설정 파일을 두고, 실제 Python 패키지는 `toa_ai/` 하위에 둡니다. 이렇게 해야 저장소 루트에서 `python -m toa_ai.cli ...` 실행이 자연스럽게 동작합니다.

## 설치

Python 3.10 이상을 권장합니다. `pip install`로 패키지와 `toa-ai` 콘솔 명령을 함께 설치합니다.

Windows PowerShell 기준:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Linux/macOS:

```bash
python -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e ".[dev]"
```

`-e`(editable)와 `[dev]`(pytest 포함)는 개발용입니다. 단순 사용이라면 `pip install .` 만으로 충분하며, 기존 방식인 `pip install -r requirements.txt`도 동작합니다.

PyTorch 설치가 환경별 CUDA/CPU 설정에 따라 실패할 수 있습니다. 그런 경우 [PyTorch 공식 설치 안내](https://pytorch.org/get-started/locally/)에 맞춰 `torch`를 먼저 설치한 뒤 `pip install -e .`를 실행하세요. CPU 전용 예시: `pip install --index-url https://download.pytorch.org/whl/cpu torch`.

설치하면 두 가지 방식으로 실행할 수 있습니다.

```bash
toa-ai --help
# 또는 (콘솔 스크립트 없이)
python -m toa_ai.cli --help
```

## 빠른 시작

아래 명령은 저장소 루트에서 실행합니다.

### 1. DB 초기화

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli init-db
```

기본 DB 경로는 `data/toa_ai/toa_memory.sqlite3`입니다.

### 2. Smoke test

합성 데이터로 전체 파이프라인을 빠르게 확인합니다.

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli smoke-test --epochs 1
```

성공하면 synthetic bar 적재, 모델 학습, promotion check, replay 결과가 JSON으로 출력됩니다. 출력 구조 예시는 다음과 같습니다(정확한 숫자는 환경·PyTorch 버전·시드에 따라 달라지며 구조만 동일). 전체 예시는 [`examples/expected_smoke_output.json`](examples/expected_smoke_output.json)에 있습니다.

```jsonc
{
  "train":     { "model_id": "...", "metrics": { "validation_loss": 1.07, "action_accuracy": 0.80, "total_samples": 1338 } },
  "promotion": { "promoted": true },
  "replay":    { "status": "ok", "decisions": 81, "orders": 0,
                 "start_equity": 10000000.0, "diagnostic_return": 0.0,
                 "profit_metrics_are_diagnostic_only": true }
}
```

직접 만든 CSV로 같은 흐름(적재 → 학습 → 리플레이)을 돌려보려면 [`examples/`](examples/)의 `sample_ohlcv.csv`와 안내를 참고하세요.

### 3. 외부 OHLCV CSV 적재

일반 OHLCV CSV 또는 Binance kline CSV/ZIP을 적재할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli ingest-external `
  --path data/external/BTCUSDT-1m.csv `
  --symbol BTCUSDT `
  --timeframe 1m `
  --market CRYPTO `
  --asset-class crypto `
  --format auto
```

Binance kline 형식임을 명시하려면:

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli ingest-external `
  --path data/external/BTCUSDT-1m.zip `
  --symbol BTCUSDT `
  --timeframe 1m `
  --format binance
```

### 4. 로컬 캐시 CSV 적재

파일명이 `BTCUSDT_5m.csv`처럼 `{symbol}_{timeframe}.csv` 형식이면 `ingest-cache`를 쓸 수 있습니다.

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli ingest-cache `
  --cache-dir data/intraday_cache `
  --timeframe 5m
```

### 5. 모델 학습

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli train `
  --timeframe 5m `
  --sequence-length 64 `
  --horizon-bars 6 `
  --epochs 4 `
  --batch-size 128 `
  --symbols BTCUSDT
```

학습 결과는 challenger 모델로 등록됩니다. 모델 파일은 기본적으로 `data/toa_ai/models/` 아래에 저장됩니다.

### 6. 리플레이

최근 challenger 또는 champion 모델로 과거 데이터를 순차 replay합니다.

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli replay `
  --model-id latest `
  --symbols BTCUSDT `
  --timeframe 5m `
  --sequence-length 64 `
  --max-episode-bars 200
```

리플레이 결과에는 다음 정보가 포함됩니다.

- decisions
- orders
- raw policy action counts
- selected action counts
- gated action counts
- gate reason counts
- accepted/rejected counts
- diagnostic return

`diagnostic_return`은 연구용 진단값이며, 모델 promote 또는 실거래 판단의 단독 기준으로 쓰면 안 됩니다.

리플레이는 기본적으로 **깨끗한(격리된) paper 계좌**에서 시작합니다. DB에 남아 있는 이전 실행의 포지션을 불러오지 않으므로, 같은 DB에서 반복 실행해도 `diagnostic_return`이 이전 상태 때문에 왜곡되지 않고 재현됩니다. 이전 포지션을 복원해 이어가려면 `--no-reset-paper-state`를 붙이세요. (실시간 누적용 `paper-once`는 항상 기존 포지션을 복원합니다.)

### 7. 모델 승격

학습된 모델이 promotion 조건을 통과하면 champion으로 승격할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli promote --model-id latest
```

promotion gate는 최소 샘플 수, validation loss, action entropy, no-action 비율 등을 확인합니다.

### 8. 상태 확인

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli status
```

DB에 저장된 symbol 목록, champion 모델, model registry를 JSON으로 확인합니다.

## CLI 명령 요약

```text
init-db          SQLite DB와 기본 schema 초기화
ingest-cache    {symbol}_{timeframe}.csv 로컬 캐시 적재
ingest-external 일반 CSV 또는 Binance kline CSV/ZIP 적재
train           GRU policy 모델 학습
promote         challenger 모델을 champion으로 승격
replay          과거 데이터 paper replay (기본 격리 계좌; --no-reset-paper-state로 복원)
paper-once      최신 bar 기준 1회 paper decision 실행
status          DB/model 상태 출력
smoke-test      합성 데이터 기반 end-to-end 점검
```

## 데이터 형식

최소 OHLCV 컬럼은 다음과 같습니다.

```csv
timestamp,open,high,low,close,volume
2026-01-01T00:00:00Z,100.0,101.0,99.5,100.5,12345
```

`timestamp`는 UTC 또는 timezone-aware 형식을 권장합니다. 일반 CSV는 `date`, `datetime`, `time`, `open_time`, `unix` 등 흔한 timestamp 컬럼명을 자동 탐색합니다.

## 안전 설계

TOA AI의 기본 방향은 “실거래 전 검증”입니다.

- `RiskConfig.allow_live_order = False`가 기본값입니다.
- 리플레이는 `PaperBroker`로만 체결을 시뮬레이션합니다.
- risk gate는 최대 포지션 수, 최대 노출, 일일 손실 제한, 최소 confidence를 검사합니다.
- 모델 수익 지표는 promotion의 단독 기준이 아니라 진단값입니다.
- `.env`, API key, 계좌번호, 토큰, DB, 모델 바이너리는 공개 저장소에 올리면 안 됩니다.

## 저장하면 안 되는 파일

오픈소스 공개 전 아래 파일과 폴더는 제외하세요.

```text
.env
.env.*
__pycache__/
data/
models/
reports/
*.sqlite
*.sqlite3
*.db
*.pt
*.pth
*.pkl
*.joblib
HOME_PC_CODEX_HANDOFF.md
```

## 개발 검증

문서 수정 또는 코드 수정 후 최소 확인:

```powershell
.\.venv\Scripts\python.exe -m compileall toa_ai
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

패키지가 정상적으로 돌아가는지 확인:

```powershell
.\.venv\Scripts\python.exe -m toa_ai.cli smoke-test --epochs 1
```

`pip install -e ".[dev]"`로 설치하면 `pytest`가 함께 들어옵니다. GitHub Actions CI(`.github/workflows/ci.yml`)가 push/PR마다 Python 3.10·3.12 환경에서 `compileall`, `pytest`, `smoke-test --epochs 1`을 자동 실행합니다.

## 한계와 주의사항

- 이 코드는 연구용 baseline입니다.
- 미래 수익, 특정 시장에서의 엣지, 실거래 안정성을 보장하지 않습니다.
- 단일 종목 long 중심 정책은 시장 국면 변화에 취약할 수 있습니다.
- `vwap_distance` 피처는 현재 전체 구간 누적 VWAP을 기준으로 계산합니다(세션/당일 anchored VWAP이 아님). 여러 날의 분봉을 넣으면 의도와 다를 수 있어 알려진 한계로 표시해 두었고, 수정하면 피처 의미가 바뀌어 재학습이 필요합니다(코드의 `TODO(vwap)` 주석 참고).
- replay 수익이 양수여도 거래비용, 슬리피지, 체결 실패, 데이터 누수, 생존편향을 별도로 검증해야 합니다.
- 실거래 연결 전에는 walk-forward out-of-sample, paper trading, 주문 제한, 장애 대응 로직을 반드시 별도로 검증해야 합니다.

## 라이선스

이 프로젝트는 BSD 2-Clause License로 공개됩니다. 자세한 내용은 `LICENSE` 파일을 확인하세요.

## 프로젝트 철학

TOA AI는 “모델이 맞췄다”보다 “검증 가능한 방식으로 틀렸는지 확인한다”를 우선합니다. 모델 구조를 복잡하게 만드는 것보다, 데이터 적재, 누수 방지, 비용 반영, replay 기록, promotion gate를 명확히 남기는 것을 더 중요하게 둡니다.
