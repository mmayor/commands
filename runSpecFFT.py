import pyaudio
import numpy as np
import pylab
import time
np.set_printoptions(suppress=True) # don't use scientific notation
import matplotlib.pyplot as plt

CHUNK = 4096 # number of data points to read at a time
RATE = 44100 # time resolution of the recording device (Hz)
TARGET = 2100 # show only this one frequency

p=pyaudio.PyAudio() # start the PyAudio class
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK) #uses default input device

# create a numpy array holding a single read of audio data
for i in range(1000): #to it a few times just to see
    t1 = time.time()
    data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
    fft = abs(np.fft.fft(data).real)
    fft = fft[:int(len(fft)/2)] # keep only first half
    freq = np.fft.fftfreq(CHUNK,1.0/RATE)
    freq = freq[:int(len(freq)/2)] # keep only first half
    assert freq[-1]>TARGET, "ERROR: increase chunk size"
    val = fft[np.where(freq>TARGET)[0][0]]

    # uncomment this if you want to see what the freq vs FFT looks like
    plt.plot(freq, fft)
    plt.axis([0, 4000, None, None])
    plt.savefig("03.png", dpi=50)
    # plt.show()
    # time.sleep()
    plt.close()

# close the stream gracefully
stream.stop_stream()
stream.close()
p.terminate()
