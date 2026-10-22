# TOA AI

OHLCV 데이터를 적재하고 GRU 정책을 학습해 과거 봉으로 리플레이하는 연구 도구입니다.

데이터와 모델, 의사결정·위험 게이트·모의 체결 기록을 SQLite에 저장합니다. [Auto Trader](https://github.com/halfsamoan/auto_trader)에서 분리한 패키지입니다.

## Install

Python 환경에서 저장소 루트에서 설치합니다. Python 버전 조건과 의존성은 [pyproject.toml](pyproject.toml)을 따릅니다.

```sh
python -m pip install .
```

## Quickstart

합성 데이터로 적재·학습·승격 검사·리플레이를 실행합니다. 외부 계좌나 API 키는 필요 없습니다.

```sh
toa-ai smoke-test --epochs 1
```

결과는 stdout에 JSON으로, 진행 로그는 stderr에 출력합니다.

## 데이터부터 리플레이까지

- **데이터 적재:** 일반 OHLCV CSV, Binance kline CSV·ZIP과 로컬 캐시를 읽습니다.
- **정책 학습:** 과거 봉의 피처로 행동·기대 수익·위험 값을 학습합니다.
- **모델 승격:** 검증 손실과 행동 분포 등 조건을 통과한 모델을 champion으로 지정합니다.
- **리플레이:** 과거 봉을 순서대로 처리하고 위험 게이트와 모의 체결을 기록합니다.

직접 만든 CSV로 실행하는 과정은 [예제](examples/README.md)에 있습니다. 전체 명령은 `toa-ai --help`로 살펴봅니다.

## 해석할 때

리플레이는 기본적으로 격리된 모의 계좌에서 시작합니다. 수익 지표는 연구용 진단값이며 모델 승격이나 실거래 판단의 단독 근거로 사용하지 않습니다.

현재 VWAP 거리 피처는 세션별이 아닌 입력 구간 누적 VWAP을 사용합니다. 여러 날의 분봉에서는 이 차이를 고려해야 합니다.

[명령·모델·개발 안내](CONTRIBUTING.md)

## License

[BSD 2-Clause](LICENSE).
