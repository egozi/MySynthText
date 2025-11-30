FROM python:3.6-slim

# ----------------------------------------------------------------------
# System dependencies
#  - build-essential, git, pkg-config: build tools
#  - SDL1.2 + addons: needed for pygame==1.9.3
#  - freetype + jpeg + zlib + portmidi: image/font/audio deps
#  - tk/tcl + X11 libs: to allow matplotlib GUI (TkAgg) to work with X11
# ----------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    pkg-config \
    libfreetype6-dev \
    libsdl1.2-dev \
    libsdl-image1.2-dev \
    libsdl-mixer1.2-dev \
    libsdl-ttf2.0-dev \
    libjpeg-dev \
    zlib1g-dev \
    libportmidi-dev \
    tk8.6 \
    tcl8.6 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
 && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------------
# Upgrade setuptools (for pkg_resources) but keep it Py3.6-compatible
# ----------------------------------------------------------------------
RUN pip install --upgrade "setuptools<=59.6.0" wheel

# ----------------------------------------------------------------------
# Workdir + clone repo
# Replace the URL with your actual MySynthText repo if different
# ----------------------------------------------------------------------
WORKDIR /opt/app

RUN git clone https://github.com/egozi/MySynthText.git

WORKDIR /opt/app/MySynthText
RUN git checkout python3

# ----------------------------------------------------------------------
# Install Python dependencies
# 1. Install the project's requirements (even if they have "modern" pins)
# 2. Then force versions known to work with Python 3.6 + pygame 1.9.3
#    - numpy 1.19.5   (last 1.x supporting Py3.6)
#    - pygame 1.9.3   (your requirement)
#    - opencv-python 4.5.4.60 (works with Py3.6 + numpy 1.19.x)
#    - matplotlib 3.3.2 (matches your original; Py3.6 OK)
#    - h5py 2.10.0, Pillow 7.2.0, reportlab 3.4.0 (Py3.6 era)
# ----------------------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt 

# # Optional: quick sanity check (can be removed to speed builds)
# RUN python - << 'EOF'
# import sys, numpy, pygame, cv2, matplotlib
# print("Python :", sys.version.split()[0])
# print("numpy  :", numpy.__version__)
# print("pygame :", pygame.version.ver)
# print("cv2    :", cv2.__version__)
# print("mpl    :", matplotlib.__version__)
# EOF

# ----------------------------------------------------------------------
# Default: drop into a shell. You can override CMD when running.
# ----------------------------------------------------------------------
CMD ["bash"]

