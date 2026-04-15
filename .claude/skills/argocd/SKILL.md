---
name: argocd
description: Scan ArgoCD application logs, triage deploy/sync issues, check container health, and diagnose migration failures across ops clusters. Use when the user says "argocd", "check deploys", "check pods", "what's failing", "triage", or asks about app health.
version: 1.0.0
---

# ArgoCD Ops Triage

## Overview

Scan and triage ArgoCD-managed applications across the ops production and staging clusters. This skill checks application sync/health status, pulls pod logs, inspects Kubernetes events, and surfaces actionable issues.

## Cluster Context

| Alias | Cluster | API Server |
|---|---|---|
| `eks-ops-production` | Production | `https://5B9C5E61FDD7E90F0CF230129CD5D4B6.gr7.us-east-2.eks.amazonaws.com` |
| `eks-ops-staging` | Staging | `https://4DB97F6B7EEB40C519A2845E2656BDFB.yl4.us-west-1.eks.amazonaws.com` |

- **Namespace:** `ops`
- **ArgoCD Server:** `argocd.flybreeze.team`

## Procedure

### Step 1: Determine Scope

Ask the user what they want to check. Options:

- **Full scan** — sweep all apps across both clusters for any issues
- **Specific app** — check a named application
- **Specific cluster** — scan only production or staging
- **Failing only** — show only apps that are degraded, out-of-sync, or have unhealthy pods

If the user's initial message already specifies scope (e.g., "check staging" or "what's failing in prod"), skip this prompt and proceed.

### Step 2: Application Status Overview

List all applications in the target scope:

```bash
argocd app list --server argocd.flybreeze.team -o wide
```

To filter by cluster, pipe through grep for the relevant API server URL. To filter by project/namespace:

```bash
argocd app list --server argocd.flybreeze.team --project ops -o wide
```

Parse the output and build a summary table with columns: **App Name**, **Sync Status**, **Health Status**, **Cluster**, **Last Sync Time**.

Flag any app where:
- Sync status is not `Synced`
- Health status is not `Healthy`

If everything is green and the user asked for a general scan, report that all apps are healthy and stop unless the user wants deeper inspection.

### Step 3: Diagnose Unhealthy Apps

For each flagged app, get detailed status:

```bash
argocd app get <app-name> --server argocd.flybreeze.team
```

This shows:
- Sync status and last sync result
- Health breakdown per resource (Deployments, Pods, Services, Jobs)
- Any sync errors or conditions

Report the resource-level health breakdown. Identify which specific resources are degraded.

### Step 4: Pull Pod Logs

For apps with unhealthy pods or containers, pull recent logs:

```bash
argocd app logs <app-name> --server argocd.flybreeze.team --namespace ops --tail 100
```

If specific container or pod names are known from Step 3, narrow the log query:

```bash
argocd app logs <app-name> --server argocd.flybreeze.team --namespace ops --container <container> --tail 150
```

For crash-looping containers, pull previous container logs:

```bash
argocd app logs <app-name> --server argocd.flybreeze.team --namespace ops --container <container> --previous --tail 150
```

Scan logs for:
- **Errors/Exceptions** — stack traces, panic messages, fatal errors
- **Migration failures** — database connection errors, schema conflicts, migration timeouts
- **OOM kills** — "OOMKilled", memory limit messages
- **Startup failures** — readiness/liveness probe failures, port binding errors
- **Connection issues** — DNS resolution failures, connection refused, timeouts to downstream services

### Step 5: Check Recent Sync History

For apps that are out-of-sync or recently failed:

```bash
argocd app history <app-name> --server argocd.flybreeze.team
```

This shows recent deploy attempts with revisions and status. Identify:
- When the last successful sync was
- What revision introduced the failure
- Whether the issue is a new regression or a persistent problem

### Step 6: Check Kubernetes Events (if needed)

If ArgoCD logs alone don't explain the issue, check resource events:

```bash
argocd app resources <app-name> --server argocd.flybreeze.team
```

This lists all managed resources and their health. For specific failing resources, the user may need `kubectl` access — note this as a next step if ArgoCD tooling isn't sufficient.

### Step 7: Triage Summary

Present findings as a structured report:

**Cluster Health Overview:**
- Total apps scanned
- Healthy / Degraded / Out-of-Sync counts

**Issues Found** (for each issue):
- **App:** name and cluster
- **Problem:** one-line summary (e.g., "CrashLoopBackOff on web container", "Sync failed — manifest validation error")
- **Evidence:** key log lines or error messages (quote directly, keep brief)
- **Likely Cause:** your assessment based on the evidence
- **Suggested Action:** concrete next step (e.g., "Roll back to revision X", "Check DB connectivity from pod", "Fix manifest at path Y")

**Migration Issues** (if any):
- Which migration step failed
- Error output
- Whether it's safe to retry or needs manual intervention

If no issues are found, confirm all apps are healthy with last-sync timestamps.

## Execution Guidelines

- Always use `--server argocd.flybreeze.team` on every `argocd` command.
- Run independent `argocd` commands in parallel where possible (e.g., fetching details for multiple apps simultaneously).
- Keep log output focused — use `--tail` to avoid dumping thousands of lines. Start with 100-150 lines; fetch more only if the issue isn't visible.
- When quoting error messages, include enough context (2-3 lines around the error) for the user to understand the failure, but don't dump entire logs.
- If `argocd` commands fail with auth errors, prompt the user to re-login: `argocd login argocd.flybreeze.team --sso`
- Timestamps matter — always note when the last successful sync was relative to now so the user knows how long things have been broken.
