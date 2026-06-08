# NACM - NeoAgent Context Manager

A lightweight local context manager for AI coding agents on low-memory devices.

## Why

AI coding agents such as Codex and Claude Code are powerful, but on low-memory laptops they may cause unnecessary repository scans, large context expansion, and heavy local I/O.

NACM helps agents work with smaller, task-focused context packs.

## Core Ideas

- Local `.agent/` workspace
- Lightweight project index
- Task-level context pack
- Codex-first prompt generation
- Low-memory device profile
- Plan / Batch / Review workflow
- No repo pollution by default

## Current Status

Early design / MVP development.

## Basic Workflow

```bash
nacm init --profile low-memory
nacm index build
nacm quick "fix image loading path issue"
nacm done
