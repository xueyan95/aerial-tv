# Vidda C1 / VL7H maintenance branch

This branch preserves the adaptation verified on a Vidda C1 (VL7H), MT9669, Android 9 / API 28. It is based on upstream commit `126579688b7e106729a8f97d2e77d2e464b6ae93` (Aerial 1.18).

## What differs

- Package: `app.orchard.tv.hisense`, versionCode 24, versionName `1.18-hisense-local.5`.
- Standard HOME entry: `app.orchard.tv.BootHomeActivity`, direct-boot aware. It waits for user unlock before opening MainActivity and accessing credential storage.
- GuardSetup skips credential-encrypted preferences before unlock.
- Input picker detects the exported Hisense source-panel service and opens the native HDMI selector.
- No usage-statistics permission or periodic foreground takeover was added. The temporary troubleshooting poller is not part of this branch.

Cold boot, physical Home, native HDMI switching, settings, voice, casting, media playback and standby/wake were confirmed on the owner's device on 2026-10-21. This does not establish compatibility with every Hisense firmware. The stock JuUI package was separately disabled with owner approval; source installation does not perform that change. Keep a device-specific rollback outside Git.

## Branches and upstream updates

`main` follows upstream; `hisense-c1` carries the adaptation. GitHub's Sync fork updates main but does not rebuild this device branch or resolve its conflicts. For an update:

```sh
git fetch origin
git switch hisense-c1
git merge origin/main
```

Here the original local checkout uses `origin` for pengchujin/aerial-tv and `fork` for xueyan95/aerial-tv. In a fresh clone of this fork, add `upstream` for pengchujin/aerial-tv and merge `upstream/main` instead.

Review conflicts in the standard manifest, GuardSetup, SystemState and app/build.gradle.kts. Preserve package identity and BootHomeActivity. Increase versionCode beyond the installed version. Build the standard release using JDK 17 and the Android SDK:

```sh
./gradlew assembleStandardRelease --console=plain
```

A successful build is not device validation. Verify Home, cold boot, HDMI, settings, voice, casting, media playback and standby/wake before calling a merged update stable. Keep the last working APK. Publish a fork release only after recording which build and device tests passed.

## Signing is essential

The existing installed custom APK was built without upstream's private signing key; the build fell back to the local Android debug keystore. Future upgrades must use the SAME signing key. Preserve that local keystore privately before rebuilding on another machine. A fresh GitHub Actions runner generates a different debug key: its APK cannot replace the current installation and preserve data.

Do not commit keystores, passwords, household IPs or device dumps. `local/` is ignored. For cloud builds, first configure an explicit release signing configuration using the existing key stored in GitHub Actions secrets, and fail the workflow if secrets are absent; never silently fall back to a newly generated debug key. No signing key has been uploaded by creating this fork.

Upstream release APKs use another package/signature and do not update this custom installation. Do not use upstream one-line install/restore tools unchanged: they target `app.orchard.tv`, not this fork. Until fork-specific installation tooling is implemented, use the privately maintained local build/update and rollback procedures.

## Scope

This fork stores the launcher source adaptation only. It does not publish household diagnostics, account data, signed device backups or system-app cleaning scripts. No upstream pull request has been submitted as part of creating this fork.

## GitHub automation

The fork default branch is `hisense-c1` so its scheduled workflow can run. `main` remains an upstream snapshot; the monitor fetches the newest stable upstream release tag directly. Every hour at minute 17 UTC, `Check upstream release` checks for a new stable release (GitHub scheduling can be delayed). It opens one PR per release; conflicts produce a draft containing a file list instead of guessing resolutions. A clean candidate triggers an unsigned build explicitly. There is no auto-merge or automatic projector deployment.

`Hisense build` runs for PRs and can be started manually. PR builds do not receive signing secrets. To produce an upgrade APK, review and merge a candidate into `hisense-c1`, then run this workflow on `hisense-c1` with `signed=true`. The existing local debug signing key is stored only as the repository Secret `HISENSE_KEYSTORE_B64`, not in Git. Signed builds verify their certificate; other build artifacts use an ephemeral runner key and cannot update the installed app. Cloud versionCode is `100000 + workflow run number`; subsequent local builds must use a higher code as well. Artifacts expire after 30 days; archive accepted releases separately.

Enable GitHub notifications for PRs and failed Actions in your personal notification settings. A PR is a notification of a pending update, not proof of a working deployment. Public repository schedules may be disabled after 60 days without repository activity; check Actions periodically or use the manual trigger to resume. Upstream prereleases and untagged commits are not monitored.
