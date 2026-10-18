/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef GPU_UNLOCK_DEVICE_PROFILE_H
#define GPU_UNLOCK_DEVICE_PROFILE_H

/* Keep the default packages restricted to RTX 3090. Other tested devices need
 * an explicit build profile, shared by enumeration and post-reset checks. */
#ifndef GPU_UNLOCK_DEVICE_ID
#define GPU_UNLOCK_DEVICE_ID 0x2204u
#endif

#if GPU_UNLOCK_DEVICE_ID == 0x2204u
#define GPU_UNLOCK_MODEL_NAME "RTX 3090"
#elif GPU_UNLOCK_DEVICE_ID == 0x2203u
#define GPU_UNLOCK_MODEL_NAME "RTX 3090 Ti"
#else
#error Unsupported GPU_UNLOCK_DEVICE_ID
#endif

#define GPU_UNLOCK_PCI_IDENTITY ((GPU_UNLOCK_DEVICE_ID << 16) | 0x10deu)

#endif
