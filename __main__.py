import subprocess
import sys
import json
import os

ENTRIES_FILE = "/tmp/niri_windows_entries.txt"

# -- EVENT HANDLERS --

def _format_event_body_windows(event_body: dict) -> str:
   data = event_body["window"]
   return "{}::{}  {} - {} \n".format(data['id'], data['workspace_id'], data['app_id'], data['title'])

def _remove_line_from_file(file_path: str, id: int|str):
   id = str(id)

   with open(file_path, 'r') as f:
      lines = f.readlines()

   with open(file_path, 'w') as f:
      for line in lines:
         if not line.startswith(id):
            f.write(line)


def on_window_opened_or_changed(event_body: dict):
   line = _format_event_body_windows(event_body)
   _remove_line_from_file(ENTRIES_FILE, event_body["window"]["id"])
   with open(ENTRIES_FILE, 'a') as f:
      f.write(line)


def on_window_closed(event_body: dict):
   id = event_body["id"]
   _remove_line_from_file(ENTRIES_FILE, id)

def entries_file_exists():
    try:
        with open(ENTRIES_FILE, 'r') as f:
            return True
    except FileNotFoundError:
        return False

# -- CORE --

DISPATCHERS ={
   "WindowOpenedOrChanged":  on_window_opened_or_changed,
   "WindowClosed": on_window_closed,
}

def read_event_stream():
    SOCKET_PATH = subprocess.run("echo $NIRI_SOCKET", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    try:
        connection = subprocess.Popen(
            ["socat", "-", f"UNIX-CONNECT:{SOCKET_PATH}"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            text=True
        )
        
        sys.stdout.flush()

        connection.stdin.write('"EventStream"\n')
        connection.stdin.flush()

        while(1):
            response = connection.stdout.readline().strip()
            response = json.loads(response)
            yield response
            print("Header:", next(iter(response.keys())))
            print("Body:", next(iter(response.values())))

            sys.stdout.flush()

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def event_dispatcher(event_header: str, event_body: dict):
   if event_header in DISPATCHERS:
      DISPATCHERS[event_header](event_body)

def __main__():
   if not entries_file_exists():
      os.system("touch /tmp/niri_windows_entries.txt")
   else:
      os.system("echo > /tmp/niri_windows_entries.txt")
   
   events = read_event_stream()

   event = next(events)
   while(event):
      event_header = next(iter(event.keys()))
      event_body = next(iter(event.values()))
      event_dispatcher(event_header, event_body)
      event = next(events)


if __name__ == "__main__":

   __main__()
