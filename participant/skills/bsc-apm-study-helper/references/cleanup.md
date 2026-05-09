# Cleanup

Optional. Once both session zips have been submitted, nothing in the study needs to stay on the participant's machine. Before any cleanup command, list the contents of the safe-storage directory and confirm both zips are present; the cleanup steps below leave that directory untouched:

```
ls -la ~/Documents/bsc-apm-submissions/
```

The listing should include `<PID>_S1_<framework>.zip` and `<PID>_S2_<framework>.zip`.

For a clean slate:

## Wipe session 2's Claude Code project state

```
ls ~/.claude/projects/
rm -rf ~/.claude/projects/<encoded>/
```

`<encoded>` is the workspace's entry under `~/.claude/projects/`. Identify it the same way as in the between-sessions reset.

## Delete the workspace

```
rm -rf <workspace>
```

## Uninstall the mock environment

Follow [in-vm-setup.md](in-vm-setup.md), Uninstall.

## Delete the participant package

Optional; the package has no further role:

```
rm -rf <participant-package>
```

The safe-storage directory and its contents are kept. After cleanup, the participant has no further use for this skill.
