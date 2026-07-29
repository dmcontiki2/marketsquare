/*
 * TOMBSTONE - content intentionally removed 2026-07-29.
 *
 * This file (_to_delete_base40_proof/ms.js) was a stray deploy-auto-commit
 * snapshot (commit a740061, 2026-07-28 18:57, "FEA-DRIFT guard: source
 * synced with live") living in a folder explicitly named for deletion. It
 * was never referenced by any app code path (verified via git grep across
 * the repo, 2026-07-29) and was only showing up as noise in the nightly
 * cost-compliance sweep.
 *
 * True deletion is not possible from this session: the Projects folder is a
 * FUSE/virtiofs mount that blocks unlink/rename for existing files (rm, mv
 * both fail with "Operation not permitted" - verified 2026-07-29). This
 * tombstone is the workaround: content zeroed out here; the original 1MB
 * content remains fully recoverable from git history at commit a740061 if
 * ever needed.
 *
 * If you are David and want this folder actually gone from disk: delete it
 * directly from Windows Explorer/Finder (outside the FUSE bridge), or run
 * `git rm -r _to_delete_base40_proof` from a native terminal on the host.
 */
