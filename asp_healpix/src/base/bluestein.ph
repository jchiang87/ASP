#ifndef __bluestein_ph__
#define __bluestein_ph__

#ifdef __cplusplus
extern "C" {
#endif

int largest_prime_factor  (int n);
int prime_factor_sum  (int n);
int nextpow2  (int n);
int good_size (int n);
void bluestein_i  (int n, double **tstorage);
void bluestein  (int n, double *data, double *tstorage, int isign);

#ifdef __cplusplus
}
#endif

#endif

