# AI Week 20a Container and Kubernetes Cheat Sheet for AI Services

Container and Kubernetes checklist for AI services:

- **Dockerfile**: multi-stage build, pinned base image, dependency lockfile, `.dockerignore`, non-root runtime user, small runtime image, no secrets or tenant data, SBOM, vulnerability scan, immutable tag.
- **Registry**: ACR/ECR/Artifact Registry with private access, vulnerability scanning, retention policy, signed/provenance-linked images, and promotion by digest.
- **Kubernetes primitives**: Deployment for rollout, Service for discovery, Ingress/Gateway for traffic, ConfigMap for non-secret config, Secret only as a reference boundary, HPA/KEDA for autoscale, PodDisruptionBudget for upgrade safety.
- **Resources**: set CPU/memory requests from measured p95 and limits from failure tests; use custom metrics for queue depth or concurrent requests when CPU is misleading.
- **Probes**: liveness checks process health; readiness checks dependencies needed to serve traffic. For RAG, `/readyz` should fail until vector store, prompt config, and model route are usable.
- **GPU node pools**: pre-approve quota in the exact region/SKU family, taint GPU nodes, tolerate only GPU workloads, and bin-pack around VRAM.

> One-liner: **a healthy AI pod is not one that started; it is one that can retrieve, call the model, honor secrets, and survive rollout without dropping traffic.**


Related: [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Reference Patterns]] · [[04 Code Snippets/AI Architecture/AI Week 20a Cloud Deployment Manifest Validator]]
