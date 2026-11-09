# Math Study System

Windows 로컬 학습 대시보드의 Phase 1 MVP입니다. 실제 학습 기록과 제출 파일은 `data/`에 저장하며, AI 채점은 아직 연결하지 않았습니다.

## 실행

```powershell
& "C:/Program Files/Python314/python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

브라우저에서 http://127.0.0.1:8765 를 엽니다. 대시보드에서 학습을 시작하고, `data/inbox/`에 JPG/JPEG/PNG/PDF를 복사하면 제출 화면에서 확인할 수 있습니다.

## iPad에서 사용

PC와 iPad를 같은 신뢰할 수 있는 사설 Wi-Fi에 연결한 뒤, PC에서 다음처럼 실행합니다.

```powershell
.\scripts\start_dashboard.ps1 -HostAddress 0.0.0.0
```

PC의 `ipconfig`에서 IPv4 주소를 확인하고 iPad Safari에서 `http://PC의IPv4주소:8765`를 엽니다. Windows 방화벽이 묻는 경우에는 사설 네트워크에서만 허용하세요. 공용 Wi-Fi나 인터넷에 포트를 공개하지 마십시오. 현재 MVP에는 로그인·TLS가 없으므로 신뢰할 수 있는 LAN에서만 사용해야 합니다.

명제·정리 카드에서 텍스트 증명을 입력하거나 Apple Pencil/손가락으로 캔버스에 작성한 뒤 `증명 검증 요청`을 누르면 제출 이력이 `PENDING_REVIEW`로 기록됩니다. 현재 Codex CLI가 연결되지 않았으므로 수학적 정답을 자동 확정하지 않습니다.

## 검증

```powershell
& "C:/Program Files/Python314/python.exe" -m pytest
```

Phase 0에서 확인된 사항: Python 3.14.3, PowerShell 사용 가능, Codex CLI는 PATH에서 미검출. 외부 배포·실제 AI 채점·Windows 작업 스케줄러 등록은 아직 구현하지 않았습니다.
