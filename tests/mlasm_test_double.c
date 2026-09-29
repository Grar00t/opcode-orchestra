/* Fault-injection double compiled against the REAL selected MLAsm header.
 * This is not an alternative inference backend and is never linked for users.
 */
#include "ml_assembly.h"
#include <fenv.h>
#include <float.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static int allocation_calls;
static int fault(const char *name) {
    const char *value=getenv("OO_TEST_FAULT");
    return value && strcmp(value,name)==0;
}
ml_error_t ml_init(void) { return fault("init") ? ML_ERROR_COMPUTATION_FAILED : ML_SUCCESS; }
void ml_cleanup(void) {}
bool ml_check_cpu_support(void) { return !fault("cpu"); }
const char *ml_get_version(void) { return fault("version") ? NULL : "test-double"; }
ml_vector_t *ml_vector_create(size_t n) {
    if (++allocation_calls==3 && fault("alloc")) return NULL;
    ml_vector_t *v=calloc(1,sizeof(*v));
    if (!v) return NULL;
    v->data=calloc(n,sizeof(float));
    if (!v->data) { free(v); return NULL; }
    v->size=v->capacity=n;v->owns_data=true;return v;
}
ml_matrix_t *ml_matrix_create(size_t rows,size_t cols) {
    if (++allocation_calls==3 && fault("alloc")) return NULL;
    if (cols!=0 && rows>SIZE_MAX/cols) return NULL;
    ml_matrix_t *m=calloc(1,sizeof(*m));
    if (!m) return NULL;
    m->data=calloc(rows*cols,sizeof(float));
    if (!m->data) { free(m); return NULL; }
    m->rows=rows;m->cols=cols;m->capacity=rows*cols;m->owns_data=true;return m;
}
void ml_vector_free(ml_vector_t *v) { free(v->data);free(v); }
void ml_matrix_free(ml_matrix_t *m) { free(m->data);free(m); }
ml_error_t ml_vector_set(ml_vector_t *v,size_t i,float f) {
    if (fault("set_vector") || i>=v->size) return ML_ERROR_INVALID_INPUT;
    v->data[i]=f;return ML_SUCCESS;
}
ml_error_t ml_matrix_set(ml_matrix_t *m,size_t r,size_t c,float f) {
    if (fault("set_matrix") || r>=m->rows || c>=m->cols) return ML_ERROR_INVALID_INPUT;
    m->data[r*m->cols+c]=f;return ML_SUCCESS;
}
ml_error_t ml_matrix_vector_mul(const ml_matrix_t *m,const ml_vector_t *v,ml_vector_t *out) {
    if (fault("matvec")) return ML_ERROR_COMPUTATION_FAILED;
    if (m->cols!=v->size || m->rows!=out->size) return ML_ERROR_DIMENSION_MISMATCH;
    for (size_t r=0;r<m->rows;++r) {
        float sum=0;
        for (size_t c=0;c<m->cols;++c) sum+=m->data[r*m->cols+c]*v->data[c];
        out->data[r]=sum;
    }
    return ML_SUCCESS;
}
ml_error_t ml_activation_softmax(const ml_vector_t *v,ml_vector_t *out) {
    if (fault("softmax")) return ML_ERROR_COMPUTATION_FAILED;
    float sum=0;
    for (size_t i=0;i<v->size;++i) { out->data[i]=expf(v->data[i]);sum+=out->data[i]; }
    for (size_t i=0;i<v->size;++i) out->data[i]/=sum;
    return ML_SUCCESS;
}
size_t ml_vector_argmax(const ml_vector_t *v) {
    if (fault("index")) return SIZE_MAX;
    size_t index=0;
    for (size_t i=1;i<v->size;++i) if (v->data[i]>v->data[index]) index=i;
    return index;
}
float ml_vector_get(const ml_vector_t *v,size_t i) {
    if (fault("nan")) return NAN;
    if (v->size==8 && fault("infinity")) return INFINITY;
    if (v->size==8 && fault("huge")) return (i&1) ? -FLT_MAX : FLT_MAX;
    return v->data[i];
}
int bridge_main(int argc,char **argv);
int main(int argc,char **argv) {
    if (fault("round_down") && fesetround(FE_DOWNWARD)!=0) return 90;
    return bridge_main(argc,argv);
}
