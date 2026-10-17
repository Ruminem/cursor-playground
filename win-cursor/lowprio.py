# SPDX-License-Identifier: Apache-2.0
"""굽기 워커 풀 — 윈도우에서는 워커를 '낮음 이하'(BELOW_NORMAL) 우선순위로 띄운다.

워커가 코어 수만큼 CPU 100% 를 몇 분 잡으면 사용자 화면 프레임이 크게 떨어졌다(2026-10-17 진도 시안 굽기, 워커 12개).
워커 수는 그대로 두고 우선순위만 낮춰 화면이 먼저 돌게 한다. 맥 · 리눅스 · CI 에서는 아무것도 안 한다.
"""
import sys
from concurrent.futures import ProcessPoolExecutor

BELOW_NORMAL = 0x4000


def low():
    """워커 initializer — 제 프로세스 우선순위를 낮춘다. 실패해도 굽기는 그대로 간다"""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        k = ctypes.windll.kernel32
        k.GetCurrentProcess.restype = wintypes.HANDLE          # 안 박으면 32비트 int 로 잘려 가짜 핸들이 깨진다
        k.SetPriorityClass.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        k.SetPriorityClass(k.GetCurrentProcess(), BELOW_NORMAL)


def pool(workers=None):
    return ProcessPoolExecutor(workers, initializer=low)


if __name__ == "__main__":
    import subprocess
    with pool(1) as p:
        pid = p.submit(__import__("os").getpid).result()
        if sys.platform == "win32":
            got = subprocess.run(["powershell", "-NoProfile", "-Command", f"(Get-Process -Id {pid}).PriorityClass"],
                                 capture_output=True, text=True).stdout.strip()
            assert got == "BelowNormal", got
            print("워커 우선순위", got)
