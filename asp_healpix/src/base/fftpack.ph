#ifndef __fftpack_ph__
#define __fftpack_ph__

#ifdef __cplusplus
extern "C" {
#endif

void cfftf (int n, double c[], double wsave[]);
void cfftb (int n, double c[], double wsave[]);
void cffti (int n, double wsave[]);
void rfftf (int n, double r[], double wsave[]);
void rfftb (int n, double r[], double wsave[]);
void rffti (int n, double wsave[]);

#ifdef __cplusplus
}
#endif

#endif

