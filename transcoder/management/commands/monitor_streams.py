import time
import threading
import psutil
from django.core.management.base import BaseCommand
from transcoder.models import Stream
from transcoder.telegram_notifier import send_channel_alert

CHECK_INTERVAL = 10  # periodic fallback (seconds)
FFMPEG_BIN = 'ffmpeg'  # used to filter processes


def extract_process_cmds():
    cmds = []
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if p.info.get('cmdline'):
                cmds.append((p.info['pid'], " ".join(p.info['cmdline'])))
        except Exception:
            continue
    return cmds


def is_stream_running(stream, process_cmds):
    try:
        source_raw = (stream.source or "").strip()
        source_norm = source_raw.lower().replace(" ", "")

        # 1) search source substring in cmdlines
        if source_norm:
            for pid, cmd in process_cmds:
                if source_norm in cmd.lower().replace(" ", ""):
                    return True

        # 2) compressed -i pattern
        input_pattern = ("-i" + source_raw).replace(" ", "").lower()
        for pid, cmd in process_cmds:
            if input_pattern in cmd.replace(" ", "").lower():
                return True

        # 3) fallback: HLS/MPD file references
        hls_file = f"/var/www/html/live/{stream.name}.m3u8"
        mpd_file = f"/var/www/html/live/{stream.name}.mpd"
        for pid, cmd in process_cmds:
            if hls_file in cmd or mpd_file in cmd:
                return True
    except Exception as e:
        print(f"[is_stream_running] ERROR for {stream.name}: {e}")
    return False


class Command(BaseCommand):
    help = "Monitors active streams and sends Telegram alerts on failure (event-driven)."

    def handle(self, *args, **options):
        print("🔍 Stream Monitor (event-driven) Started...")
        # Force initial DB state True so first real scan will generate alerts for dead streams
        Stream.objects.update(is_running=True)

        # Start background watcher thread that waits for ffmpeg exits
        stop_event = threading.Event()
        watcher = threading.Thread(target=self._ffmpeg_watcher_loop, args=(stop_event,), daemon=True)
        watcher.start()

        try:
            # Main loop: we still run periodic scans as a fallback
            while True:
                self.run_monitor_cycle()
                # sleep small amount but break earlier if watcher triggered immediate scan
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            stop_event.set()
            print("🛑 Monitor stopped manually")
        except Exception as e:
            stop_event.set()
            print("[monitor] CRITICAL ERROR:", e)

    def _ffmpeg_watcher_loop(self, stop_event):
        """
        Build a dynamic list of ffmpeg psutil.Process objects and block with psutil.wait_procs.
        When any ffmpeg process dies, trigger an immediate scan by calling run_monitor_cycle().
        """
        while not stop_event.is_set():
            # collect ffmpeg processes (only those that look like ffmpeg)
            ffmpeg_procs = []
            for p in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    # filter by process name or cmdline containing 'ffmpeg'
                    name = (p.info.get('name') or "").lower()
                    cmd = " ".join(p.info.get('cmdline') or []).lower()
                    if 'ffmpeg' in name or 'ffmpeg' in cmd:
                        ffmpeg_procs.append(p)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not ffmpeg_procs:
                # nothing to wait on, sleep small time to avoid busy-loop
                time.sleep(1)
                continue

            # wait until any of these processes terminate or for timeout
            try:
                ended, alive = psutil.wait_procs(ffmpeg_procs, timeout=5)
                if ended:
                    # One or more ffmpeg processes ended — run immediate cycle
                    print(f"[watcher] detected {len(ended)} ffmpeg exit(s); triggering immediate scan")
                    try:
                        self.run_monitor_cycle()
                    except Exception as e:
                        print("[watcher] run_monitor_cycle error:", e)
                # loop continues and rebuilds the ffmpeg_procs list
            except Exception as e:
                # If wait_procs fails, sleep and rebuild
                print("[watcher] wait_procs error:", e)
                time.sleep(1)

    def run_monitor_cycle(self):
        process_cmds = extract_process_cmds()
        print(f"[monitor] captured {len(process_cmds)} process cmdlines")
        for stream in Stream.objects.all():
            detected = is_stream_running(stream, process_cmds)
            print(f"[monitor] Stream: {stream.name} | DB: {stream.is_running} | Detected: {detected}")

            # immediate STOP alert if detected False and previously marked running
            if not detected and stream.is_running:
                print(f"[monitor] STOP detected on {stream.name} → sending Telegram alert")
                send_channel_alert(stream.name, 'stopped')

            # update DB & send START alert on change
            if stream.is_running != detected:
                stream.is_running = detected
                stream.save(update_fields=['is_running'])
                if detected:
                    print(f"[monitor] START detected on {stream.name} → sending Telegram alert")
                    send_channel_alert(stream.name, 'running')
                    self.stdout.write(self.style.SUCCESS(f"✅ {stream.name} STARTED"))
                else:
                    self.stdout.write(self.style.ERROR(f"❌ {stream.name} STOPPED"))

