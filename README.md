# ScreenShare-Project

## Dependencies

Install the Python packages used by the client:

```bash
pip install -r requirements.txt
```

On Linux, tkinter is usually provided by the system package manager, not pip. If the client still fails with No module named 'tkinter', install the OS package for your Python build, for example:

```bash
sudo apt-get install python3-tk
```

The client uses the headless OpenCV build because it only needs camera capture and image encoding, not OpenCV GUI windows.