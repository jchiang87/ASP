#ifndef __ls_fft_ph__
#define __ls_fft_ph__

#ifdef __cplusplus
extern "C" {
#endif

complex_plan make_complex_plan  (int length);
void kill_complex_plan  (complex_plan plan);
void complex_plan_forward  (complex_plan plan, double *data);
void complex_plan_backward  (complex_plan plan, double *data);
real_plan make_real_plan  (int length);
void kill_real_plan  (real_plan plan);
void real_plan_forward_fftpack  (real_plan plan, double *data);
void real_plan_forward_fftw  (real_plan plan, double *data);
void real_plan_backward_fftpack  (real_plan plan, double *data);
void real_plan_backward_fftw  (real_plan plan, double *data);
void real_plan_forward_c  (real_plan plan, double *data);
void real_plan_backward_c  (real_plan plan, double *data);

#ifdef __cplusplus
}
#endif

#endif

