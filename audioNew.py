#!python
import numpy as np
import scikits.audiolab as audiolab
import pylab as plt
import mel
from scipy.fftpack import dct
sound=audiolab.sndfile('prueba.wav')
data=sound.read_frames(sound.get_samplerate())
data=data[:,0]
mfccs=[]
for i in range(len(data)/512-1):
    win=data[512*i:512*i+1024]
    s=np.fft.rfft(win*ham,512)
    p=(s.real**2+s.imag**2)/len(win)
    m=np.log(np.dot(p,mel.MELfilterbank_speech).clip(1e-5,np.inf))
    d=dct(m)
    mfcc=d[1:13]
    mfccs.append(mfcc)
plt.imshow(np.array(mfccs).T)
plt.show()