import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SyncHandler(FileSystemEventHandler):
    def __init__(self, local_dir, remote_dir, remote_host):
        self.local_dir = local_dir
        self.remote_dir = remote_dir
        self.remote_host = remote_host

    def sync_folders(self):
        """Synchronize local folder with the remote folder using rsync."""
        try:
            subprocess.run(
                [
                    "rsync",
                    "-e", "ssh -p 2022",  # Use custom SSH port
                    "-a",
                    self.local_dir,
                    f"{self.remote_host}:{self.remote_dir}"
                ],
                check=True
            )
            print("Sync complete.")
        except subprocess.CalledProcessError as e:
            print(f"Error during rsync: {e}")

    def on_any_event(self, event):
        """Trigger synchronization on any file system event."""
        print(f"Detected change: {event.src_path}")
        self.sync_folders()

if __name__ == "__main__":
    # Local and remote configuration
    local_dir = "/home/intermidia/enoe-otavio/Server/images"  # Replace with your local folder path
    remote_dir = "~/enoe-backup"  # Replace with your remote folder path
    remote_host = "enoe@enoe.icmc.usp.br"  # Replace with your remote user and host

    # Ensure local directory ends with a slash for rsync compatibility
    if not local_dir.endswith('/'):
        local_dir += '/'

    # Create event handler and observer
    event_handler = SyncHandler(local_dir, remote_dir, remote_host)
    observer = Observer()
    observer.schedule(event_handler, local_dir, recursive=True)

    # Start monitoring
    try:
        print(f"Monitoring changes in {local_dir}...")
        observer.start()
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping the monitor...")
        observer.stop()
    observer.join()

    # rsync -e 'ssh -p 2022' -a Server/images enoe@enoe.icmc.usp.br:~/enoe-backup