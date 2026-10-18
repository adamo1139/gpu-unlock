# Experimental RTX 3090 Ti validation

**Code changes, review and result analysis/write-up: GPT-6.1 Sol (Codex).
Results were measured on physical hardware.**

An RTX 3090 was successfully patched and benchmarked first. The same unlock
sequence was then applied to an RTX 3090 Ti and tested.

One RTX 3090 Ti completed a cold-boot trial with selector readback, successful
FLR, driver initialization and CUDA compute. No Xid was observed during testing.

Environment: Ubuntu kernel `7.0.0-38-generic`, an existing modified NVIDIA
`610.43.02` driver, pinned `610.43.03` firmware, and a custom initramfs hook
ordered before udev. Driver and benchmark sources were unchanged between runs.
Model services remained resident.

## Measurements at 450 W

cuBLAS 12.0.2 dense GEMM, `M=N=K=8192`, FP32 accumulation/output,
reduced-precision reductions disabled. Ten warmups, five approximately 250 ms
samples; medians below count `2*M*N*K` operations.

| Input | Before (TFLOPS) | After (TFLOPS) | Change |
|---|---:|---:|---:|
| FP16 | 87.46 | 118.39 | +35.4% |
| BF16 | 87.50 | 157.41 | +79.9% |
| TF32 | 42.58 | 82.61 | +94.0% |

PyTorch `2.13.0+cu130` causal Flash Attention: batch 1, 32 heads, head dimension
128, sequence 4096, explicitly selected Flash backend; five-sample medians:

| Input | Before (ms) | After (ms) | Time reduction |
|---|---:|---:|---:|
| FP16 | 1.9309 | 1.3636 | 29.4% |
| BF16 | 1.8986 | 1.3007 | 31.5% |

The full runs covered 21 GEMM and 12 attention configurations. GEMM
sample-output checks matched; attention outputs were finite. Maximum GPU
temperature was 66 C before and 68 C after.

## Validation scope

Both profiles compile and pass host tests, including 58 mocked transaction
scenarios per profile with the pinned assets. The hardware trial used the same
device-ID selection and unlock sequence before the final name/test cleanup;
the final binary has been build/host-tested but not cold-booted again.

This is one-board, short-duration validation. Other environments, packaged
boot integration and persistent Ti selection across DKMS rebuilds remain
unvalidated.
