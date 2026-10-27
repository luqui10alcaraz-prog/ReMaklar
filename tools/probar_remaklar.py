"""Visible, bounded performance trial from immutable original Jaguar state.

Run with Probar-ReMaklar.bat on Windows, or directly under WSL.
"""
from pathlib import Path
import argparse
import csv
import datetime
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def hmp(port, command):
    with socket.create_connection(('127.0.0.1', port), timeout=2) as connection:
        connection.settimeout(10)
        def receive():
            data = b''
            while not data.endswith(b'(qemu) '):
                chunk = connection.recv(65536)
                if not chunk:
                    raise ConnectionError('QEMU cerro el monitor')
                data += chunk
            return data.decode(errors='replace')
        receive()
        connection.sendall((command + '\n').encode())
        return receive()

def process_usage(pid):
    text = Path('/proc/%d/stat' % pid).read_text()
    fields = text[text.rfind(')') + 2:].split()
    ticks = int(fields[11]) + int(fields[12])
    rss_mb = int(fields[21]) * os.sysconf('SC_PAGE_SIZE') / 1024 ** 2
    return ticks / os.sysconf('SC_CLK_TCK'), rss_mb

def free_port():
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        return listener.getsockname()[1]

def main():
    p = argparse.ArgumentParser(description='Prueba real de ReMaklar 0.11 en una copia nueva.')
    p.add_argument('--estado', choices=('marco', 'final'), default='marco',
                   help='marco: observar el repintado; final: ventana ya dibujada')
    p.add_argument('--limite', type=int, default=180, help='segundos de prueba, 10..600 (180 por defecto)')
    p.add_argument('--comprobar', action='store_true', help='verificar requisitos sin iniciar una VM')
    p.add_argument('--sin-ventana', action='store_true', help=argparse.SUPPRESS)
    a = p.parse_args()
    if not 10 <= a.limite <= 600:
        p.error('--limite debe estar entre 10 y 600 segundos')
    os.chdir(ROOT)
    for program in ('qemu-system-i386', 'qemu-img'):
        subprocess.run([program, '--version'], check=True, capture_output=True, timeout=5)
    if not a.sin_ventana and not a.comprobar and not os.environ.get('DISPLAY'):
        raise RuntimeError('No hay DISPLAY de WSLg. Ejecuta el BAT desde tu sesion de Windows.')
    checkpoint = 'window102-first' if a.estado == 'marco' else 'window102-painted'
    manifest = ROOT / ('reports/graphics-011/resume-validation/%s-machine-checkpoint.json' % checkpoint)
    record = json.loads(manifest.read_text())
    for filename, expected in record['files'].items():
        assert (ROOT / filename).stat().st_size == expected['bytes'], filename
    assert (ROOT / 'build/graphics009-recovery.iso').is_file()
    print('Requisitos OK. Checkpoint: %s. RAM: 512 MB. CPU: Pentium III emulado.' % checkpoint, flush=True)
    if a.comprobar:
        print('Comprobacion sin iniciar VM completada. Los hashes completos se verifican al abrir la prueba.')
        return 0
    label = 'prueba-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + str(os.getpid())
    out = ROOT / ('logs/graphics-011-restore-' + label)
    port = free_port()
    print('Preparando una copia nueva y verificando hashes. Puede tardar unos segundos.', flush=True)
    launch = [sys.executable, 'tools/restore_graphics011_checkpoint.py',
              '--from-label', checkpoint, '--as-label', label, '--port', str(port),
              '--display', 'none' if a.sin_ventana else 'gtk']
    subprocess.run(launch, check=True, timeout=120)
    pid = int((out / 'pid').read_text())
    running = True
    reason = 'limite_de_tiempo'
    samples = []
    frames = []
    started = None
    interrupted = False
    def on_signal(signum, frame):
        nonlocal interrupted
        interrupted = True
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, on_signal)
    def capture(stem, elapsed):
        ppm = out / (stem + '.ppm')
        hmp(port, 'screendump ' + json.dumps(str(ppm)))
        im = Image.open(ppm)
        digest = hashlib.sha256(im.tobytes()).hexdigest()
        if not frames or frames[-1]['rgb_sha256'] != digest or stem == 'final':
            png = out / (stem + '.png')
            im.save(png)
            frames.append({'elapsed_seconds': round(elapsed, 3), 'png': str(png.relative_to(ROOT)), 'rgb_sha256': digest})
        return digest
    try:
        capture('inicio', 0)
        resume = hmp(port, 'cont')
        status = hmp(port, 'info status')
        (out / 'resume-status.txt').write_text(resume + status)
        if 'VM status: running' not in status:
            raise RuntimeError('La VM no se reanudo; revisar resume-status.txt')
        started = previous_time = time.monotonic()
        previous_cpu, _ = process_usage(pid)
        print('\nVM en marcha. Cierra la ventana de QEMU para terminar; Ctrl+C tambien detiene esta copia.', flush=True)
        print('Limite: %d s. La entrada de teclado/mouse es experimental y puede detener WindowServer.' % a.limite, flush=True)
        print('El repintado es real. Esta compilacion conserva las trazas de diagnostico activas.', flush=True)
        print('Logs y capturas: ' + str(out), flush=True)
        with (out / 'rendimiento.csv').open('w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['elapsed_seconds', 'host_cpu_percent_one_core', 'host_rss_mb'])
            next_capture = 5
            while time.monotonic() - started < a.limite:
                if interrupted:
                    reason = 'interrumpida_por_usuario'
                    break
                time.sleep(1)
                now = time.monotonic()
                try:
                    cpu, rss = process_usage(pid)
                except FileNotFoundError:
                    running = False
                    reason = 'ventana_cerrada_o_qemu_finalizado'
                    break
                elapsed = now - started
                row = [round(elapsed, 3), round(100 * (cpu - previous_cpu) / (now - previous_time), 2), round(rss, 2)]
                writer.writerow(row)
                csv_file.flush()
                samples.append(row)
                previous_time, previous_cpu = now, cpu
                if elapsed >= next_capture:
                    try:
                        capture('frame-%03d' % elapsed, elapsed)
                    except (OSError, ConnectionError):
                        running = False
                        reason = 'ventana_cerrada_o_qemu_finalizado'
                        break
                    print('%5.0f s | CPU host: %5.1f%% de un nucleo | RAM host: %.0f MB' % tuple(row), flush=True)
                    next_capture += 5
    finally:
        elapsed = 0 if started is None else time.monotonic() - started
        if running:
            try:
                hmp(port, 'stop')
                capture('final', elapsed)
                hmp(port, 'pmemsave 0xfd000000 3145728 ' + json.dumps(str(out / 'final.vram')))
                subprocess.run([sys.executable, 'tools/inspect_graphics011_live.py',
                                str((out / 'diagnostico').relative_to(ROOT)), '--port', str(port), '--logs',
                                '--pids', '2523,2528,2533,2535', '--tail-bytes', '20000'],
                               check=True, timeout=40, capture_output=True)
            except (OSError, ConnectionError, subprocess.SubprocessError) as error:
                detail = getattr(error, 'stderr', None)
                (out / 'diagnostico-error.txt').write_text(str(error) + '\n' + (detail.decode(errors='replace') if isinstance(detail, bytes) else str(detail or '')))
            finally:
                try:
                    hmp(port, 'quit')
                except (OSError, ConnectionError):
                    pass
        summary = {'checkpoint': checkpoint, 'qemu_pid': pid, 'monitor': port,
                   'reason': reason, 'wall_seconds_after_resume': round(elapsed, 3),
                   'cpu_mean_percent_one_core': round(sum(r[1] for r in samples) / len(samples), 2) if samples else None,
                   'host_rss_peak_mb': max((r[2] for r in samples), default=None),
                   'frames': frames,
                   'measurement_notes': 'CPU/RSS del proceso QEMU en el host. Captura cada 5 s, no es un contador FPS. Trazas guest activas. El arnes original conserva su propio limite y puede cerrar los servicios.',
                   'preserved_checkpoints_modified': False}
        (out / 'resumen.json').write_text(json.dumps(summary, indent=2) + '\n')
        print('\nPrueba terminada: %s. Duracion activa: %.1f s.' % (reason, elapsed), flush=True)
        print('Resultados: ' + str(out), flush=True)
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, AssertionError, subprocess.SubprocessError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        sys.exit(1)
