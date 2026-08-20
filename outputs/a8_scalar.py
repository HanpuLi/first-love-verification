import librosa, numpy as np
CUT_IN=4742.0; CUT_OUT=4768.0; OFF=4730.0
y,sr=librosa.load("seg_48k_mono.wav",sr=48000)
def scal(a,b):
    i0=int(round((a-OFF)*sr)); i1=int(round((b-OFF)*sr))
    seg=y[i0:i1]; return float(np.sqrt(np.mean(seg**2)))
E_pre,E_post=0.129644557833672,0.198803529143333
# try symmetric windows of various widths around the cut
for w in [0.25,0.5,1.0,2.0,5.0]:
    pre=scal(CUT_IN-w,CUT_IN); post=scal(CUT_IN,CUT_IN+w)
    print(f"win {w:>4}s  pre={pre:.15f} post={post:.15f} surge={(post/pre-1)*100:.6f}%")
print("essay:        pre=0.129644557833672 post=0.198803529143333 surge=53.345062%")
# cut-out
print("--- cut-out ---")
for w in [0.25,0.5,1.0,2.0,5.0]:
    pre=scal(CUT_OUT-w,CUT_OUT); post=scal(CUT_OUT,CUT_OUT+w)
    print(f"win {w:>4}s  pre={pre:.15f} post={post:.15f} chg={(post/pre-1)*100:.6f}%")
print("essay:        pre=0.288493871688843 post=0.286753028631210 chg=-0.603425%")
